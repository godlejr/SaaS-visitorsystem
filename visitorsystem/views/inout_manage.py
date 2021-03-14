from flask import Blueprint

inout_manage = Blueprint('inout_manage', __name__)

import datetime

from flask import Blueprint, current_app, render_template, request, jsonify
from flask_login import current_user
from sqlalchemy import and_, or_
from math import ceil

from loggers import log
from visitorsystem.lib.auth_decorators import visit_admin_required

from visitorsystem.forms import Pagination
from visitorsystem.models import db, Vcapplymaster, Sccode, Sccompinfo, Vcapplyuser, \
    Ssctenant, Vcinoutinfo, Scclass, Scuser

inout_tag = Blueprint('inout_tag', __name__)


@inout_manage.route('/', methods=['GET', 'POST'], defaults={'page': 1})
@inout_manage.route('/page/<int:page>')
@visit_admin_required
def index(page):
    siteList = db.session.query(Sccode).join(Scclass, Scclass.id == Sccode.class_id) \
        .filter(and_(Scclass.class_cd == 'SITE', Scclass.use_yn == '1',
                     Sccode.tenant_id == current_user.ssctenant.id, Sccode.use_yn == '1')).all()

    visitCategory = db.session.query(Sccode).filter(
        and_(Sccode.tenant_id == current_user.ssctenant.id, Sccode.class_id == '6', Sccode.use_yn == '1')).all()

    today = datetime.datetime.now()
    end_date = today
    start_date = today - datetime.timedelta(days=7)

    searchCondition = {
        'visit_sdate': request.args.get('visit_sdate', str(start_date.strftime('%Y-%m-%d'))),
        'visit_edate': request.args.get('visit_edate', str(end_date.strftime('%Y-%m-%d'))),
        'visit_category': request.args.get('visit_category', 'all'),
        'visit_user': request.args.get('visit_user', ''),
        'visit_interviewer': request.args.get('visit_interviewer', ''),
        'visit_purpose': request.args.get('visit_purpose', ''),
        'visit_dept': request.args.get('visit_dept', ''),
        'comp_nm': request.args.get('comp_nm', ''),
        'page': request.args.get('page', page),
        'pages': request.args.get('pages', 10),
        'site_id': request.args.get('site_id', 'all')
    }

    searchResult = getVisitorListBySearchCondition(searchCondition)
    log("Transaction").info("[tenant_id:%s][login_id:%s]", current_user.ssctenant.id, current_user.id)

    return render_template(current_app.config['TEMPLATE_THEME'] + '/inout_manage/list.html',
                           current_app=current_app,
                           visitCategory=visitCategory,
                           lists=searchResult['visitorList'],
                           pagination=searchResult['pagination'],
                           query_string=request.query_string.decode('utf-8'),
                           siteList=siteList,
                           userAuth=searchResult['userAuth'])


@inout_manage.route('/search', methods=['POST'])
@visit_admin_required
def search():
    if request.method == 'POST':
        # 조회조건에 맞게 조회
        searchResult = getVisitorListBySearchCondition(request.form)
        pagination = searchResult['pagination']
        log("Transaction").info("[tenant_id:%s][login_id:%s]", current_user.ssctenant.id, current_user.id)

        lists = []
        for row in searchResult['visitorList']:
            out_time = row.out_time
            if row.out_time is None:
                out_time = ''

            results = {
                "master_id": row.id,
                "user_id": row.vcapplyuser.id,
                "comp_nm": row.vcapplyuser.vcapplymaster.sccompinfo.comp_nm,
                "visit_category": row.vcapplyuser.vcapplymaster.visit_category,
                "visit_purpose": row.vcapplyuser.vcapplymaster.visit_purpose,
                "visit_user": row.vcapplyuser.visitant,
                "visit_interviewr": row.vcapplyuser.vcapplymaster.interviewr,
                "visit_sdate": row.in_time,
                "visit_edate": out_time,
                "site_nm": row.site_nm,
                "site_nm2": row.in_area_nm,
                "visit_dept": row.vcapplyuser.vcapplymaster.get_interviewer.dept_nm,
            }
            lists.append(results)

        page_iter = []
        for page in pagination.iter_pages():
            page_iter.append(page)

        return jsonify({'msg': lists,
                        'listSize': searchResult['listSize'],
                        'pagination': pagination.serializable(page_iter, searchResult['p_pages']),
                        'query_string': "request.query_string.decode('utf-8')",
                        'searchCondition': request.form,
                        'userAuth': searchResult['userAuth']})


# 조회조건에 맞게 방문신청리스트 SELECT Function
def getVisitorListBySearchCondition(searchCondition):
    page = int(searchCondition['page'])
    pages = int(searchCondition['pages'])
    offset = (pages * (page - 1)) if page != 1 else 0

    # 로그인한 사용자 권한에 따른 조회 데이터 변경 (계정당 권한 1개)
    userAuth = current_user.get_auth.code

    visitorList = db.session.query(Vcinoutinfo).join(Vcapplyuser).join(Vcapplymaster).filter(
        Vcinoutinfo.tenant_id == current_user.ssctenant.id, Vcapplymaster.tenant_id == current_user.ssctenant.id,
        Vcapplymaster.tenant_id == current_user.ssctenant.id,
        Vcapplyuser.id == Vcinoutinfo.apply_user_id, Vcapplymaster.id == Vcapplyuser.apply_id,
        Vcinoutinfo.use_yn == '1', Vcapplymaster.use_yn == '1', Vcapplyuser.use_yn == '1').order_by(
        Vcinoutinfo.in_time.desc())

    # AUTH_VISIT_ADMIN: 본인 사업장만 조회
    if userAuth == current_app.config['AUTH_VISIT_ADMIN']:
        visitorList = visitorList.filter(Vcinoutinfo.site_nm == current_user.site_nm)

    # AUTH_ADMIN : 전체관리자 - 사업장 다봐야함
    if userAuth == current_app.config['AUTH_ADMIN']:
        if searchCondition['site_id'] != "all":
            visitorList = visitorList.filter(Vcinoutinfo.site_id == searchCondition['site_id'])

    if searchCondition['visit_category'] != "all":
        visitorList = visitorList.filter(Vcapplymaster.visit_category == searchCondition['visit_category'])

    if searchCondition['visit_purpose'] != '':
        visitorList = visitorList.filter(
            Vcapplymaster.visit_purpose.like("%" + searchCondition['visit_purpose'] + "%"))

    if searchCondition['comp_nm'] != '':
        visitorList = visitorList.join(Sccompinfo).filter(Vcapplymaster.biz_id == Sccompinfo.id,
                                                          Sccompinfo.comp_nm.like(
                                                              "%" + searchCondition['comp_nm'] + "%"))

    if searchCondition['visit_user'] != '':
        visitorList = visitorList.filter(Vcapplyuser.visitant == searchCondition['visit_user'])

    if searchCondition['visit_interviewer'] != '':
        visitorList = visitorList.filter(Vcapplymaster.interviewr == searchCondition['visit_interviewer'])

    if searchCondition['visit_dept'] != '':
        visitorList = visitorList.join(Scuser).filter(Scuser.id == Vcapplymaster.interview_id,
                                                      Scuser.dept_nm.like(
                                                          "%" + searchCondition['visit_dept'] + "%"))

    if searchCondition['visit_sdate'] != "" and searchCondition['visit_edate'] != "":
        condition_edate = datetime.datetime.strptime(searchCondition['visit_edate'], '%Y-%m-%d')
        condition_edate = str(condition_edate + datetime.timedelta(days=1))
        visitorList = visitorList.filter(and_(Vcinoutinfo.in_time >= searchCondition['visit_sdate'],
                                              Vcinoutinfo.in_time <= condition_edate))

    listCount = visitorList.count()
    pagination = Pagination(page, pages, listCount)
    # 페이지 개수
    p_pages = int(ceil(visitorList.count() / float(pages)))

    visitorList = visitorList.limit(pages).offset(offset).all()

    return {'pagination': pagination,
            'p_pages': p_pages,
            'visitorList': visitorList,
            'listSize': listCount,
            'userAuth': userAuth}


@inout_manage.route('/save/users/<int:user_id>', methods=['GET', 'POST'])
def save(user_id):
    ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()
    applyuser = db.session.query(Vcapplyuser).filter(Vcapplyuser.id == user_id).first()

    today = datetime.datetime.now()
    today_day = str(today.strftime('%Y-%m-%d'))
    tomorrow = today + datetime.timedelta(days=1)
    tomorrow_day = str(tomorrow.strftime('%Y-%m-%d'))
    barcode = applyuser.barcode
    if barcode is None or barcode == '':
        return jsonify({'msg': '발급이 취소된 QR코드 입니다.'})

    else:
        start_date = applyuser.start_date
        end_date = applyuser.end_date
        if start_date > today_day or end_date < today_day:
            return jsonify({'msg': '방문 기간이 아닙니다. 방문기간 : ' + start_date + ' ~ ' + end_date + ''})

    vcInoutInfo = db.session.query(Vcinoutinfo).filter(Vcinoutinfo.apply_user_id == user_id,
                                                       Vcinoutinfo.in_time >= today_day,
                                                       Vcinoutinfo.in_time < tomorrow_day).order_by(
        Vcinoutinfo.in_time.desc()).first()

    if vcInoutInfo != None:
        out_std_date = today - datetime.timedelta(minutes=5)

        if vcInoutInfo.out_time == None and vcInoutInfo.in_time <= out_std_date:
            vcInoutInfo.out_time = today
            vcInoutInfo.out_area_nm = applyuser.vcapplymaster.site_nm2
            vcInoutInfo.out_area_cd = applyuser.vcapplymaster.site_id2
            db.session.commit()
            return jsonify({'msg': '퇴장 확인이 되었습니다.'})
        else:
            if vcInoutInfo.out_time != None:
                return jsonify({'msg': '이미 되장 확인이 되었습니다.'})

        return jsonify({'msg': '이미 방문 확인이 되었습니다'})

    else:

        inoutInfo = Vcinoutinfo()
        inoutInfo.tenant_id = ssctenant.id
        inoutInfo.apply_user_id = applyuser.id
        inoutInfo.site_nm = applyuser.vcapplymaster.site_nm
        inoutInfo.site_id = applyuser.vcapplymaster.site_id
        # 들어온 정문
        inoutInfo.in_area_nm = applyuser.vcapplymaster.site_nm2
        inoutInfo.in_area_cd = applyuser.vcapplymaster.site_id2
        inoutInfo.in_time = today

        db.session.add(inoutInfo)
        db.session.commit()

        return jsonify({'msg': '환영합니다.'})
