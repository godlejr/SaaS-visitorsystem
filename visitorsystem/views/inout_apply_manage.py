import datetime
from math import ceil

from flask import Blueprint, current_app, render_template, request, jsonify
from flask_login import current_user
from sqlalchemy import and_

from loggers import log
from visitorsystem.forms import Pagination
from visitorsystem.models import db, Vcapplymaster, Sccode, Sccompinfo, Scrule, Vcvisituser, ScRuleFile, Scclass, Scuser

inout_apply_manage = Blueprint('inout_apply_manage', __name__)


@inout_apply_manage.route('/', methods=['GET', 'POST'], defaults={'page': 1})
@inout_apply_manage.route('/page/<int:page>')
def index(page):
    visitCategory = db.session.query(Sccode).filter(
        and_(Sccode.tenant_id == current_user.ssctenant.id, Sccode.class_id == '6', Sccode.use_yn == '1')).all()

    siteList = db.session.query(Sccode).join(Scclass, Scclass.id == Sccode.class_id) \
        .filter(and_(Scclass.class_cd == 'SITE', Scclass.use_yn == '1',
                     Sccode.tenant_id == current_user.ssctenant.id, Sccode.use_yn == '1')).all()
    today = datetime.datetime.now()
    end_date = today
    start_date = today - datetime.timedelta(days=7)

    searchCondition = {
        'applicant_name': request.args.get('applicant_name', ''),
        'applicant_phone': request.args.get('applicant_phone', ''),
        'visit_sdate': request.args.get('visit_sdate', str(start_date.strftime('%Y-%m-%d'))),
        'visit_edate': request.args.get('visit_edate', str(end_date.strftime('%Y-%m-%d'))),
        'visit_category': request.args.get('visit_category', 'all'),
        'approval_state': request.args.get('approval_state', 'all'),
        'visit_purpose': request.args.get('visit_purpose', ''),
        'comp_nm': request.args.get('comp_nm', ''),
        'page': request.args.get('page', page),
        'pages': request.args.get('pages', 10),
        'site_id': request.args.get('site_id', 'all')
    }

    searchResult = getApplyListBySearchCondition(searchCondition)
    log("Transaction").info("[tenant_id:%s][login_id:%s]", current_user.ssctenant.id, current_user.id)

    return render_template(current_app.config['TEMPLATE_THEME'] + '/inout_apply_manage/list.html',
                           current_app=current_app,
                           visitCategory=visitCategory,
                           lists=searchResult['applyList'],
                           pagination=searchResult['pagination'],
                           query_string=request.query_string.decode('utf-8'),
                           siteList=siteList,
                           userAuth=searchResult['userAuth'])


# ??????????????? Modal
@inout_apply_manage.route('/applicant/search', methods=['POST'])
def applicantSearch():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id
        name = request.form['visitInput']
        lists = []

        if len(name) == 0:
            return jsonify({'msg': lists});

        for row in db.session.query(Scuser).filter(
                db.and_(Scuser.tenant_id == tenant_id, Scuser.name.like(name + '%'), Scuser.user_type == '1',
                        Scuser.use_yn == '1')):
            scuser = {
                "name": row.name,
                "phone": row.phone,
                "comp_nm": row.sccompinfo.comp_nm,
                "biz_no": row.sccompinfo.biz_no
            }
            lists.append(scuser)

        return jsonify({'msg': lists});


@inout_apply_manage.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        # ??????????????? ?????? ??????
        searchResult = getApplyListBySearchCondition(request.form)
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
                        'query_string': "request.query_string.decode('utf-8')",
                        'searchCondition': request.form,
                        'userAuth': searchResult['userAuth']})


@inout_apply_manage.route('/save', methods=['POST'])
def save():
    approval_date = request.form['approval_date']
    approval_state = request.form['approval_state']
    lists = request.form.getlist("lists[]")

    # checkList??? ????????? row ????????? ????????????
    db.session.query(Vcapplymaster).session.query(Vcapplymaster).filter(Vcapplymaster.id.in_(lists),
                                                                        Vcapplymaster.tenant_id == current_user.ssctenant.id) \
        .update({"approval_state": approval_state, "approval_date": approval_date}, synchronize_session=False)
    db.session.commit()

    return jsonify({'msg': '??????????????? ?????????????????????.',
                    'approval_state': approval_state,
                    'lists': lists})


@inout_apply_manage.route('/detail', methods=['POST'])
def detail():
    # ?????? ID??? ?????? ????????? ?????? ???????????? ??????
    id = request.form['id']
    visit_sdate = request.form['sdate']
    visit_edate = request.form['edate']

    # 1. ????????? ?????? ID??? ?????? ????????? ?????? ??? Rule ?????? ?????? ?????? (Vcstackuser)
    selectApplyInfo = db.session.query(Vcvisituser).join(Scrule, Vcvisituser.rule_id == Scrule.id). \
        filter(and_(Vcvisituser.tenant_id == current_user.ssctenant.id, Vcvisituser.apply_id == id, \
                    Vcvisituser.use_yn == '1', Scrule.use_yn == '1'))

    # 2. ????????? ?????? ID??? ????????? ????????? User ?????????
    users = []
    for row in selectApplyInfo.group_by(Vcvisituser.name, Vcvisituser.phone, Vcvisituser.apply_id,
                                        Vcvisituser.apply_id).all():
        results = {
            "id": row.id,
            "name": row.name,
            "phone": row.phone,
            "apply_id": row.apply_id
        }
        users.append(results)

    # 3. ??????????????? Rule??? ???????????? ?????? ??? ?????? ??????
    bucketUrl = current_app.config['S3_BUCKET_NAME_VMS']

    RuleInfolist = []
    for row in selectApplyInfo.all():
        # ????????? ????????? ???????????????, ?????? or ??????
        if row.text_desc == "":
            scrulefile = db.session.query(ScRuleFile).filter(db.and_(ScRuleFile.tenant_id == current_user.ssctenant.id,
                                                                     ScRuleFile.use_yn == '1',
                                                                     ScRuleFile.visit_id == row.id)).first()
            # ????????? Type??? ???????????? ??????, ?????? ???????????? ???????????? ???????????? ?????? (?????? ??? Type??????)
            # ??????
            if scrulefile == None:
                ruleType = '??????'
                if (visit_sdate >= row.s_date) and (visit_edate <= row.e_date):
                    ruleRes = '??????'
                else:
                    ruleRes = '??????'
            # ??????
            else:
                ruleType = '??????'
                if scrulefile.s3_url != '':
                    ruleRes = '??????'
                    ruleDesc = bucketUrl + scrulefile.s3_url
                else:
                    ruleRes = '??????'
                    ruleDesc = ''
        else:
            ruleType = '?????????'
            ruleDesc = row.text_desc
            ruleRes = '??????'

        results = {
            "id": row.id,  # User ID
            "apply_id": row.apply_id,  # ???????????? ID
            "name": row.name,  # ????????? ??????
            "phone": row.phone,  # ????????? ?????????
            "rule_id": row.rule_id,  # Rule ID
            "rule_name": row.scrule.rule_name,  # Rule ??????
            "rule_type": ruleType,  # Rule Type
            "rule_duedate": row.scrule.rule_duedate,  # Rule ??????
            "s_date": row.s_date,  # ?????? Rule ?????????
            "e_date": row.e_date,  # ?????? Rule ?????????
            "ruleRes": ruleRes,  # ????????? ???????????? ???????????? ??????
            "ruleDesc": ruleDesc  # ????????? ?????? or s3 url ?????????
        }
        RuleInfolist.append(results)

    return jsonify({'users': users,
                    'userRuleInfoList': RuleInfolist})


# ??????????????? ?????? ????????????????????? SELECT Function
def getApplyListBySearchCondition(searchCondition):
    page = int(searchCondition['page'])
    pages = int(searchCondition['pages'])
    offset = (pages * (page - 1)) if page != 1 else 0

    # ???????????? ????????? ????????? ?????? ?????? ????????? ?????? (????????? ?????? 1???)
    userAuth = current_user.get_auth.code

    # ?????? ???????????? ????????? Data ????????? ?????? ??????. (?????? Data Select???????????? type ????????? ??????)
    selectApplyLists = db.session.query(Vcapplymaster)




    if userAuth == current_app.config['AUTH_VISITOR']:
        selectApplyLists = db.session.query(Vcapplymaster).filter(
            and_(Vcapplymaster.use_yn == '1', Vcapplymaster.tenant_id == current_user.ssctenant.id,
                 Vcapplymaster.applicant == current_user.name, Vcapplymaster.phone == current_user.phone)) \
            .order_by(Vcapplymaster.id.desc())

    # AUTH_ADMIN, AUTH_VISIT_ADMIN : ?????? ???????????? ??????????????? ??? ??? ??????
    # AUTH_APPROVAL : ???????????? ?????? ??? ??????????????? ??? ??? ??????
    else :
        if userAuth == current_app.config['AUTH_ADMIN']:
            selectApplyLists = db.session.query(Vcapplymaster).filter(
                and_(Vcapplymaster.use_yn == '1', Vcapplymaster.tenant_id == current_user.ssctenant.id)) \
                .order_by(Vcapplymaster.id.desc())


        elif userAuth == current_app.config['AUTH_APPROVAL']:
            selectApplyLists = db.session.query(Vcapplymaster).filter(
                and_(Vcapplymaster.use_yn == '1', Vcapplymaster.interview_id == current_user.id,
                     Vcapplymaster.tenant_id == current_user.ssctenant.id)).order_by(Vcapplymaster.id.desc())

        elif userAuth == current_app.config['AUTH_VISIT_ADMIN']:
            selectApplyLists = db.session.query(Vcapplymaster).filter(
                and_(Vcapplymaster.use_yn == '1', Vcapplymaster.tenant_id == current_user.ssctenant.id,
                     Vcapplymaster.site_nm == current_user.site_nm)) \
                .order_by(Vcapplymaster.id.desc())


        applicant_name = searchCondition['applicant_name']
        applicant_phone = searchCondition['applicant_phone']
        if applicant_name != '' and applicant_phone:
            selectApplyLists = selectApplyLists.filter(Vcapplymaster.applicant == applicant_name, Vcapplymaster.phone == applicant_phone)

    # AUTH_ADMIN : ??????????????? - ????????? ????????????
    # AUTH_APPROVAL : ????????????- ????????? ???????????? ???????????? ?????? ??? ?????? ??????
    # AUTH_VISIT_ADMIN : ??????????????? - ???????????????
    if (userAuth == current_app.config['AUTH_ADMIN']) or (userAuth == current_app.config['AUTH_APPROVAL']):
        if searchCondition['site_id'] != "all":
            selectApplyLists = selectApplyLists.filter(Vcapplymaster.site_id == searchCondition['site_id'])
    # elif (userAuth == current_app.config['AUTH_VISIT_ADMIN']):

    # ??????????????? ?????? ??????
    if searchCondition['visit_category'] != "all":
        selectApplyLists = selectApplyLists.filter(Vcapplymaster.visit_category == searchCondition['visit_category'])
    if searchCondition['approval_state'] != "all":
        selectApplyLists = selectApplyLists.filter(Vcapplymaster.approval_state == searchCondition['approval_state'])
    if searchCondition['visit_purpose'] != '':
        selectApplyLists = selectApplyLists.filter(
            Vcapplymaster.visit_purpose.like("%" + searchCondition['visit_purpose'] + "%"))
    if searchCondition['comp_nm'] != '':
        selectApplyLists = selectApplyLists.join(Sccompinfo).filter(Vcapplymaster.biz_id == Sccompinfo.id,
                                                                    Sccompinfo.comp_nm.like(
                                                                        "%" + searchCondition['comp_nm'] + "%"))
    if searchCondition['visit_sdate'] != "" and searchCondition['visit_edate'] != "":
        condition_edate = datetime.datetime.strptime(searchCondition['visit_edate'], '%Y-%m-%d')
        condition_edate = str(condition_edate + datetime.timedelta(days=1))
        selectApplyLists = selectApplyLists.filter(and_(Vcapplymaster.created_at >= searchCondition['visit_sdate'],
                                                        Vcapplymaster.created_at <= condition_edate))

    pagination = Pagination(page, pages, selectApplyLists.count())
    # ????????? ??????
    p_pages = int(ceil(selectApplyLists.count() / float(pages)))

    applyList = selectApplyLists.limit(pages).offset(offset).all()

    return {'pagination': pagination,
            'p_pages': p_pages,
            'applyList': applyList,
            'listSize': selectApplyLists.count(),
            'userAuth': userAuth}
