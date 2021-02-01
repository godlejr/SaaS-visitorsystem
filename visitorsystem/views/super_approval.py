from flask import Blueprint, current_app, render_template, request
from sqlalchemy import or_

from visitorsystem.forms import superApprovalSearchForm
from visitorsystem.models import db, User, Professional,Ssctenant, Vcapplymaster, Vcapplyuser

super_approval = Blueprint('super_approval', __name__)


@super_approval.context_processor
def utility_processor():
    def url_for_s3(s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))

    return dict(url_for_s3=url_for_s3)


@super_approval.route('/', methods=['GET', 'POST'])
def index():
    ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()
    form = superApprovalSearchForm(request.form)

    if request.method == 'GET':
        applyList = Vcapplymaster.query.all()

        return render_template(current_app.config['TEMPLATE_THEME'] + '/super_approval/list.html',
                               current_app=current_app,
                               ssctenant=ssctenant,
                               applyList=applyList,
                               form=form)

    #supervisory_approve.html 에서 조회조건 쿼리 수행 부분
    if request.method == 'POST':
        #조회조건 쿼리 (객체를 받아와 필터)
        vcApplyMasterQuery = Vcapplymaster.query
        visit_category = request.form["visit_category"]
        approval_state = request.form["approval_state"]
        visit_sdate = request.form["visit_sdate"]
        visit_edate = request.form["visit_edate"]
        #박정은 날짜 포맷변경필요 '%m/%d/%Y' to '%y/%m/%d'

        print("=======조회조건=========")
        print(visit_sdate)
        print(visit_edate)
        print(visit_category)
        print(approval_state)

        if visit_category != "all":
            vcApplyMasterQuery = vcApplyMasterQuery.filter(Vcapplymaster.visit_category == visit_category)

        if approval_state != "all":
            vcApplyMasterQuery = vcApplyMasterQuery.filter(Vcapplymaster.approval_state == approval_state)

        if visit_sdate != "" and visit_edate != "":
            vcApplyMasterQuery = vcApplyMasterQuery.filter(Vcapplymaster.visit_sdate >= visit_sdate, Vcapplymaster.visit_edate <= visit_edate)

        print("=======Query=========")
        print(vcApplyMasterQuery)

        #회사명 검색도 될 수 있도록 설정 필요
        applyList = vcApplyMasterQuery.filter(Vcapplymaster.apply_nm.like("%" + form.apply_nm.data + "%")).all()
                                           # applyList.apply_nm.like("%" + form.apply_nm.data + "%")).all()

        return render_template(current_app.config['TEMPLATE_THEME'] + '/super_approval/list.html',
                               current_app=current_app,
                               ssctenant=ssctenant,
                               applyList=applyList,
                               form=form)
