import datetime
from flask import Blueprint, current_app, render_template, request, session, jsonify
from flask_login import current_user
from math import ceil
from sqlalchemy import and_

from loggers import log
from visitorsystem.forms import Pagination
from visitorsystem.models import db, Ssctenant, Vcapplymaster, Sccode, Sccompinfo, Scrule, Vcvisituser, ScRuleFile

super_approval = Blueprint('super_approval', __name__)

@super_approval.route('/', methods=['GET', 'POST'], defaults={'page': 1})
@super_approval.route('/page/<int:page>')
def index(page):
    visitCategory = db.session.query(Sccode).filter(
        and_(Sccode.tenant_id == current_user.ssctenant.id, Sccode.class_id == '6', Sccode.use_yn == '1')).all()

    today = datetime.datetime.now()
    end_date = today + datetime.timedelta(days=7)

    searchCondition = {
        'visit_sdate': request.args.get('visit_sdate', str(today.strftime('%Y-%m-%d'))),
        'visit_edate': request.args.get('visit_edate', str(end_date.strftime('%Y-%m-%d'))),
        'visit_category': request.args.get('visit_category', 'all'),
        'approval_state': request.args.get('approval_state', 'all'),
        'visit_purpose': request.args.get('visit_purpose', ''),
        'comp_nm': request.args.get('comp_nm', ''),
        'page': request.args.get('page', page),
        'pages': request.args.get('pages', 10)
    }

    searchResult = selectApplyListWithSearchCondition(searchCondition)
    log("Transaction").info("[tenant_id:%s][login_id:%s]", current_user.ssctenant.id, current_user.id)

    return render_template(current_app.config['TEMPLATE_THEME'] + '/super_approval/list.html',
                           current_app=current_app,
                           visitCategory=visitCategory,
                           lists=searchResult['applyList'],
                           pagination=searchResult['pagination'],
                           query_string=request.query_string.decode('utf-8'))


@super_approval.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        #조회조건에 맞게 조회
        searchResult = selectApplyListWithSearchCondition(request.form)
        pagination = searchResult['pagination']
        log("Transaction").info("[tenant_id:%s][login_id:%s]", current_user.ssctenant.id, current_user.id)

        lists = []
        for row in searchResult['applyList']:
            results = {
                "id": row.id,
                "comp_nm": row.sccompinfo.comp_nm,
                "visit_category": row.visit_category,
                "visit_purpose": row.visit_purpose,
                "applicant": row.applicant,
                "visit_sdate": row.visit_sdate,
                "visit_edate": row.visit_edate,
                "site_nm": row.site_nm,
                "site_nm2": row.site_nm2,
                "approval_state": row.approval_state,
            }
            lists.append(results)

        page_iter = []
        for page in pagination.iter_pages():
            page_iter.append(page)

        return jsonify({'msg': lists,
                        'listSize': searchResult['listSize'],
                        'pagination': pagination.serializable(page_iter, searchResult['p_pages']),
                        'query_string': "request.query_string.decode('utf-8')"})


@super_approval.route('/save', methods=['POST'])
def save():
    approval_date = request.form['approval_date'];
    approval_state = request.form['approval_state']
    lists = request.form.getlist("lists[]")

    #checkList에 포한된 row 승인값 업데이트
    db.session.query(Vcapplymaster).session.query(Vcapplymaster).filter(Vcapplymaster.id.in_(lists)) \
        .update({"approval_state": approval_state, "approval_date": approval_date}, synchronize_session=False)
    db.session.commit()

    return jsonify({'msg': '성공적으로 처리되었습니다.',
                    'approval_state': approval_state,
                    'lists': lists})


@super_approval.route('/detail', methods=['POST'])
def detail():
    # 작업 ID에 대한 출입자 명단 상세정보 출력
    id = request.form['id']
    visit_sdate = request.form['sdate']
    visit_edate = request.form['edate']

    # 1. 선택한 작업 ID에 속한 사용자 명단 및 Rule 정보 전체 추출 (Vcstackuser)
    selectApplyInfo = db.session.query(Vcvisituser).join(Scrule, Vcvisituser.rule_id == Scrule.id).\
                                        filter(and_(Vcvisituser.tenant_id == current_user.ssctenant.id, Vcvisituser.apply_id == id, \
                                        Vcvisituser.use_yn == '1', Scrule.use_yn == '1'))

    # 2. 선택한 작업 ID에 포함된 방문자 User 리스트
    users = []
    for row in selectApplyInfo.group_by(Vcvisituser.name, Vcvisituser.phone, Vcvisituser.apply_id).all():
        results = {
            "id":row.id,
            "name": row.name,
            "phone":row.phone,
            "apply_id":row.apply_id
        }
        users.append(results)

    # 3. 사용자들의 Rule이 유효한지 판단 및 정보 저장
    bucketUrl = current_app.config['S3_BUCKET_NAME_VMS']

    RuleInfolist = []
    for row in selectApplyInfo.all():
        #규칙 타입이 파일 경우 s3 경로 Setting
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
             #달력 규칙이 유효한지 만료인지 기간 검증
            if (visit_sdate >= row.s_date) and (visit_edate <= row.e_date):
                 ruleRes = '가능'
            else:
                 ruleRes = '불가'

        results = {
            "id":row.id,                             #User ID
            "apply_id": row.apply_id,                #출입신청 ID
            "name": row.name,                        #방문자 이름
            "phone": row.phone,                      #방문자 핸드폰
            "rule_id": row.rule_id,                  #Rule ID
            "rule_name": row.scrule.rule_name,       #Rule 명칭
            "rule_type": row.scrule.rule_type,       #Rule Type
            "rule_duedate": row.scrule.rule_duedate, #Rule 기간
            "s_date": row.s_date,                    #달력 Rule 시작일
            "e_date":row.e_date,                     #달력 Rule 종료일
            "ruleRes": ruleRes,                      #규칙이 유효한지 만료인지 표기
            "ruleDesc": ruleDesc                     #텍스트 규칙 or s3 url 입력값
        }
        RuleInfolist.append(results)

    return jsonify({'users': users,
                    'userRuleInfoList': RuleInfolist})


# 조회조건에 맞게 출입신청리스트 SELECT Function
def selectApplyListWithSearchCondition(searchCondition):
    page = int(searchCondition['page'])
    pages = int(searchCondition['pages'])
    offset = (pages * (page - 1)) if page != 1 else 0

    # 로그인한 사용자 권한에 따른 조회 데이터 변경 (계정당 권한 1개)
    userAuth = current_user.get_auth.code

    #일반 사용자는 조회는 Data 없도록 하기 위함. (없는 Data Select함으로써 type 형태만 갖춤)
    selectApplyLists = db.session.query(Vcapplymaster)

    if (userAuth == current_app.config['AUTH_ADMIN']) or (userAuth == current_app.config['AUTH_VISIT_ADMIN']):
        selectApplyLists = db.session.query(Vcapplymaster).filter(Vcapplymaster.use_yn == 1).order_by(Vcapplymaster.id.desc())
    elif userAuth == current_app.config['AUTH_APPROVAL']:
        selectApplyLists = db.session.query(Vcapplymaster).filter(and_(Vcapplymaster.use_yn == 1, Vcapplymaster.interview_id == current_user.id)).order_by(Vcapplymaster.id.desc())

    # 조회조건에 따른 쿼리
    if searchCondition['visit_category'] != "all":
        selectApplyLists = selectApplyLists.filter(Vcapplymaster.visit_category == searchCondition['visit_category'])
    if searchCondition['approval_state'] != "all":
        selectApplyLists = selectApplyLists.filter(Vcapplymaster.approval_state == searchCondition['approval_state'])
    if searchCondition['visit_purpose'] != '':
        selectApplyLists = selectApplyLists.filter(Vcapplymaster.visit_purpose.like("%" + searchCondition['visit_purpose'] + "%"))
    if searchCondition['comp_nm'] != '':
        selectApplyLists = selectApplyLists.join(Sccompinfo).filter(Sccompinfo.comp_nm.like("%" + searchCondition['comp_nm'] + "%"))
    if searchCondition['visit_sdate'] != "" and searchCondition['visit_edate'] != "":
        selectApplyLists = selectApplyLists.filter(and_(Vcapplymaster.created_at >= searchCondition['visit_sdate'], Vcapplymaster.created_at <= searchCondition['visit_edate']))

    pagination = Pagination(page, pages, selectApplyLists.count())
    #페이지 개수
    p_pages = int(ceil(selectApplyLists.count() / float(pages)))

    applyList = selectApplyLists.limit(pages).offset(offset).all()

    return {'pagination' : pagination,
            'p_pages': p_pages,
            'applyList': applyList,
            'listSize': selectApplyLists.count()}
