import logging

from flask import Blueprint, current_app, render_template, request, url_for, redirect
from sqlalchemy import or_

from flask_login import current_user, login_required
from visitorsystem.forms import superApprovalSearchForm, Pagination
from visitorsystem.models import db, User, Professional,Ssctenant, Vcapplymaster
from loggers import log

super_approval = Blueprint('super_approval', __name__)

@super_approval.route('/', methods=['GET', 'POST'])
def index():
    print("super_approval.index 진입")
    ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()
    form = superApprovalSearchForm(request.form)

    if request.method == 'GET':
        applyList = Vcapplymaster.query.all()
        print("super_approval.index Get 진입")
        log("Transaction").info("[tenant_id:%s][login_id:%s]", ssctenant.tenant_id, current_user.id)

        return render_template(current_app.config['TEMPLATE_THEME'] + '/super_approval/list.html',
                               current_app=current_app,
                               ssctenant=ssctenant,
                               applyList=applyList,
                               form=form)

    #supervisory_approve.html 에서 조회조건 쿼리 수행 부분
    if request.method == 'POST':
        print("super_approval.index Post 진입")
        #조회조건 쿼리 (객체를 받아와 필터)
        vcApplyMasterQuery = Vcapplymaster.query
        visit_category = request.form["visit_category"]
        approval_state = request.form["approval_state"]
        visit_sdate = request.form["visit_sdate"]
        visit_edate = request.form["visit_edate"]
        #박정은 날짜 포맷변경필요 '%m/%d/%Y' to '%y/%m/%d'

        if visit_category != "all":
            vcApplyMasterQuery = vcApplyMasterQuery.filter(Vcapplymaster.visit_category == visit_category)

        if approval_state != "all":
            vcApplyMasterQuery = vcApplyMasterQuery.filter(Vcapplymaster.approval_state == approval_state)

        if visit_sdate != "" and visit_edate != "":
            vcApplyMasterQuery = vcApplyMasterQuery.filter(Vcapplymaster.visit_sdate >= visit_sdate, Vcapplymaster.visit_edate <= visit_edate)

        #회사명 검색도 될 수 있도록 설정 필요
        applyList = vcApplyMasterQuery.filter(Vcapplymaster.visit_purpose.like("%" + form.visit_purpose.data + "%")).all()
                                           # applyList.apply_nm.like("%" + form.apply_nm.data + "%")).all()

        log("Transaction").info("[tenant_id:%s][login_id:%s]", ssctenant.tenant_id, current_user.id)

        return render_template(current_app.config['TEMPLATE_THEME'] + '/super_approval/list.html',
                               current_app=current_app,
                               ssctenant=ssctenant,
                               applyList=applyList,
                               form=form)


@super_approval.route('/list', defaults={'page': 1})
@super_approval.route('/list/page/<int:page>')
def list(page):
    ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()

    applyList = Vcapplymaster.query

    page = page
    pages = 15
    # Pagination pram : page, per_page, total_count
    pagination = Pagination(page, pages, applyList.count())

    if page != 1:
        offset = pages * (page - 1)
    else:
        offset = 0

    return render_template(current_app.config['TEMPLATE_THEME'] + '/super_approval/list.html',
                           current_app=current_app,
                           ssctenant=ssctenant,
                           applyList=applyList,
                           pagination=pagination,
                           query_string=request.query_string.decode('utf-8'))

# @super_approval.route('/detail')
# def detail(id):
#     # 작업 참여자 인원 SELECT
