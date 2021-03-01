import datetime

from flask import Blueprint, current_app, render_template, request, jsonify
from flask_login import current_user
from sqlalchemy import and_, or_
from math import ceil

from loggers import log
from visitorsystem.lib.auth_decorators import visit_admin_required

from visitorsystem.forms import Pagination
from visitorsystem.notification import publish_message
from visitorsystem.models import db, Vcapplymaster, Sccode, Sccompinfo, Scrule, Vcvisituser, ScRuleFile, Vcapplyuser, \
    Ssctenant

inout_tag = Blueprint('inout_tag', __name__)


@inout_tag.route('/', methods=['GET', 'POST'], defaults={'page': 1})
@inout_tag.route('/page/<int:page>')
@visit_admin_required
def index(page):
    visitCategory = db.session.query(Sccode).filter(
        and_(Sccode.tenant_id == current_user.ssctenant.id, Sccode.class_id == '6', Sccode.use_yn == '1')).all()

    today = datetime.datetime.now()
    end_date = today
    start_date = today - datetime.timedelta(days=7)

    searchCondition = {
        'admin_sdate': request.args.get('admin_sdate', str(start_date.strftime('%Y-%m-%d'))),
        'admin_edate': request.args.get('admin_edate', str(end_date.strftime('%Y-%m-%d'))),
        'visit_category': request.args.get('visit_category', 'all'),
        'visit_user': request.args.get('visit_user', ''),
        'visit_interviewer': request.args.get('visit_interviewer', ''),
        'visit_purpose': request.args.get('visit_purpose', ''),
        'barcode_state': request.args.get('barcode_state', 'all'),
        'comp_nm': request.args.get('comp_nm', ''),
        'page': request.args.get('page', page),
        'pages': request.args.get('pages', 10)
    }

    searchResult = getApplyVisitorListBySearchCondition(searchCondition)
    log("Transaction").info("[tenant_id:%s][login_id:%s]", current_user.ssctenant.id, current_user.id)

    return render_template(current_app.config['TEMPLATE_THEME'] + '/inout_tag/list.html',
                           current_app=current_app,
                           visitCategory=visitCategory,
                           lists=searchResult['applyVisitorList'],
                           pagination=searchResult['pagination'],
                           query_string=request.query_string.decode('utf-8'))


@inout_tag.route('/search', methods=['POST'])
@visit_admin_required
def search():
    if request.method == 'POST':
        # 조회조건에 맞게 조회
        searchResult = getApplyVisitorListBySearchCondition(request.form)
        pagination = searchResult['pagination']
        log("Transaction").info("[tenant_id:%s][login_id:%s]", current_user.ssctenant.id, current_user.id)

        lists = []
        for row in searchResult['applyVisitorList']:

            barcode_state = '미발급'
            if row.barcode is not None and row.barcode != '':
                barcode_state = '발급'

            results = {
                "master_id": row.vcapplymaster.id,
                "user_id": row.id,
                "comp_nm": row.vcapplymaster.sccompinfo.comp_nm,
                "visit_category": row.vcapplymaster.visit_category,
                "visit_purpose": row.vcapplymaster.visit_purpose,
                "visit_user": row.visitant,
                "visit_interviewr": row.vcapplymaster.interviewr,
                "visit_sdate": row.vcapplymaster.visit_sdate,
                "visit_edate": row.vcapplymaster.visit_edate,
                "site_nm": row.vcapplymaster.site_nm,
                "site_nm2": row.vcapplymaster.site_nm2,
                "barcode_state": barcode_state,
            }
            lists.append(results)

        page_iter = []
        for page in pagination.iter_pages():
            page_iter.append(page)

        return jsonify({'msg': lists,
                        'listSize': searchResult['listSize'],
                        'pagination': pagination.serializable(page_iter, searchResult['p_pages']),
                        'query_string': "request.query_string.decode('utf-8')"})



@inout_tag.route('/detail', methods=['POST'])
def detail():
    # 작업 ID에 대한 출입자 명단 상세정보 출력
    id = request.form['id']
    applyUserId = request.form['user_id']
    visit_sdate = request.form['sdate']
    visit_edate = request.form['edate']

    applyUser = db.session.query(Vcapplyuser).filter(Vcapplyuser.id == applyUserId).first()

    # 1. 선택한 작업 ID에 속한 사용자 명단 및 Rule 정보 전체 추출 (Vcstackuser)
    selectApplyInfo = db.session.query(Vcvisituser).join(Scrule, Vcvisituser.rule_id == Scrule.id). \
        filter(and_(Vcvisituser.tenant_id == current_user.ssctenant.id,
                    Vcvisituser.apply_id == id, Vcvisituser.phone == applyUser.phone,
                    Vcvisituser.name == applyUser.visitant,
                    Vcvisituser.use_yn == '1', Scrule.use_yn == '1'))

    # 2. 선택한 작업 ID에 포함된 방문자 User 리스트
    users = []
    results = {
        "id": 1,
        "name": applyUser.visitant,
        "phone": applyUser.phone,
        "apply_id": id
    }
    users.append(results)

    # 3. 사용자들의 Rule이 유효한지 판단 및 정보 저장
    bucketUrl = current_app.config['S3_BUCKET_NAME_VMS']

    RuleInfolist = []
    for row in selectApplyInfo.all():
        # 규칙 타입이 파일 경우 s3 경로 Setting
        if row.scrule.rule_type == "파일":
            scrulefile = db.session.query(ScRuleFile).filter(db.and_(ScRuleFile.tenant_id == current_user.ssctenant.id,
                                                                     ScRuleFile.use_yn == '1',
                                                                     ScRuleFile.visit_id == row.id)).first()
            scrulefile.s3_url
            if scrulefile.s3_url != '':
                ruleRes = '가능'
                ruleDesc = bucketUrl + scrulefile.s3_url
            else:
                ruleRes = '불가'
                ruleDesc = ''

        elif row.scrule.rule_type == "텍스트":
            ruleDesc = row.text_desc

            if ruleDesc != '':
                ruleRes = '가능'
            else:
                ruleRes = '불가'

        elif row.scrule.rule_type == "달력":
            # 달력 규칙이 유효한지 만료인지 기간 검증
            if (visit_sdate >= row.s_date) and (visit_edate <= row.e_date):
                ruleRes = '가능'
            else:
                ruleRes = '불가'

        results = {
            "id": row.id,  # User ID
            "apply_id": row.apply_id,  # 출입신청 ID
            "name": row.name,  # 방문자 이름
            "phone": row.phone,  # 방문자 핸드폰
            "rule_id": row.rule_id,  # Rule ID
            "rule_name": row.scrule.rule_name,  # Rule 명칭
            "rule_type": row.scrule.rule_type,  # Rule Type
            "rule_duedate": row.scrule.rule_duedate,  # Rule 기간
            "s_date": row.s_date,  # 달력 Rule 시작일
            "e_date": row.e_date,  # 달력 Rule 종료일
            "ruleRes": ruleRes,  # 규칙이 유효한지 만료인지 표기
            "ruleDesc": ruleDesc  # 텍스트 규칙 or s3 url 입력값
        }
        RuleInfolist.append(results)

    return jsonify({'users': users,
                    'userRuleInfoList': RuleInfolist})


@inout_tag.route('users/<int:id>/qrcode')
def qrcode(id):
    ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()
    applyuser = db.session.query(Vcapplyuser).filter(Vcapplyuser.id == id).first()


    return render_template(current_app.config['TEMPLATE_THEME'] + '/inout_tag/visitor_tag.html',
                           current_app=current_app,applyuser=applyuser,ssctenant=ssctenant)


@inout_tag.route('/save', methods=['POST'])
def save():
    barcode_sdate = request.form['barcode_sdate']
    barcode_state = request.form['barcode_state'].strip()

    barcode = ''
    event_url = current_user.ssctenant.event_url + '/inoutTag/users'

    lists = request.form.getlist("lists[]")

    if barcode_state == '발급':
        for id in lists:
            applyuser = db.session.query(Vcapplyuser).filter(Vcapplyuser.id == id,
                                                             Vcapplyuser.tenant_id == current_user.ssctenant.id).first()
            applyuser.start_date = barcode_sdate
            applyuser.barcode = event_url + '/' + id + '/qrcode'
            applyuser.barcode_type = 'QRcode'
            applyuser.end_date = applyuser.vcapplymaster.visit_sdate

            message = event_url + '/' + id + '/qrcode' + '            링크를 클릭하여 QR코드를 확인하세요 -' + current_user.ssctenant.comp_nm
            publish_message(applyuser.phone, message)
            db.session.commit()

    else:
        # checkList에 포한된 row 승인값 업데이트
        db.session.query(Vcapplyuser).filter(Vcapplyuser.id.in_(lists)) \
            .update({"start_date": '', "barcode": '',
                     "barcode_type": '', "end_date": ''},
                    synchronize_session=False)
        db.session.commit()

    return jsonify({'msg': '성공적으로 ' + barcode_state + '처리되었습니다.',
                    'barcode_state': barcode_state,
                    'lists': lists})


# 조회조건에 맞게 출입신청리스트 SELECT Function
def getApplyVisitorListBySearchCondition(searchCondition):
    page = int(searchCondition['page'])
    pages = int(searchCondition['pages'])
    offset = (pages * (page - 1)) if page != 1 else 0

    # 로그인한 사용자 권한에 따른 조회 데이터 변경 (계정당 권한 1개)
    userAuth = current_user.get_auth.code

    applyVisitorList = db.session.query(Vcapplyuser).join(Vcapplymaster).filter(
        Vcapplymaster.tenant_id == current_user.ssctenant.id, Vcapplyuser.tenant_id == current_user.ssctenant.id,
        Vcapplymaster.id == Vcapplyuser.apply_id, Vcapplymaster.use_yn == 1,
        Vcapplymaster.approval_state == '승인').order_by(
        Vcapplymaster.id.desc())

    # 본인 사업장만 조회
    if userAuth == current_app.config['AUTH_VISIT_ADMIN']:
        applyVisitorList = applyVisitorList.filter(Vcapplymaster.site_nm == current_user.site_nm)

    # 조회조건에 따른 쿼리
    if searchCondition['barcode_state'] != "all":
        status = searchCondition['barcode_state'].strip()
        if status == '발급':
            applyVisitorList = applyVisitorList.filter(and_(Vcapplyuser.barcode != '', Vcapplyuser.barcode is not None))
        else:
            applyVisitorList = applyVisitorList.filter(or_(Vcapplyuser.barcode == '', Vcapplyuser.barcode == None))

    if searchCondition['visit_category'] != "all":
        applyVisitorList = applyVisitorList.filter(Vcapplymaster.visit_category == searchCondition['visit_category'])

    if searchCondition['visit_purpose'] != '':
        applyVisitorList = applyVisitorList.filter(
            Vcapplymaster.visit_purpose.like("%" + searchCondition['visit_purpose'] + "%"))

    if searchCondition['comp_nm'] != '':
        applyVisitorList = applyVisitorList.join(Sccompinfo).filter(Vcapplymaster.biz_id == Sccompinfo.id,
                                                                    Sccompinfo.comp_nm.like(
                                                                        "%" + searchCondition['comp_nm'] + "%"))

    if searchCondition['visit_user'] != '':
        applyVisitorList = applyVisitorList.filter(
            Vcapplyuser.visitant == searchCondition['visit_user'])

    if searchCondition['visit_interviewer'] != '':
        applyVisitorList = applyVisitorList.filter(
            Vcapplymaster.interviewr == searchCondition['visit_interviewer'])

    if searchCondition['admin_sdate'] != "" and searchCondition['admin_edate'] != "":
        applyVisitorList = applyVisitorList.filter(and_(Vcapplymaster.approval_date >= searchCondition['admin_sdate'],
                                                        Vcapplymaster.approval_date <= searchCondition['admin_edate']))

    listCount = applyVisitorList.count()
    pagination = Pagination(page, pages, listCount)
    # 페이지 개수
    p_pages = int(ceil(applyVisitorList.count() / float(pages)))

    applyVisitorList = applyVisitorList.limit(pages).offset(offset).all()

    return {'pagination': pagination,
            'p_pages': p_pages,
            'applyVisitorList': applyVisitorList,
            'listSize': listCount}
