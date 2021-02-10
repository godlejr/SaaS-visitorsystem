import logging

from flask import Blueprint, current_app, render_template, request, url_for, redirect, session
from sqlalchemy import or_, and_

from flask_login import current_user, login_required
from visitorsystem.forms import superApprovalSearchForm, Pagination
from visitorsystem.models import db, User, Professional,Ssctenant, Vcapplymaster, Sccode
from loggers import log

super_approval = Blueprint('super_approval', __name__)

@super_approval.route('/', methods=['GET', 'POST'], defaults={'page': 1})
@super_approval.route('/page/<int:page>')
def index(page):
    ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()
    visitCategory = Sccode.query.filter(and_(Sccode.tenant_id == session['tenant_id'], Sccode.class_id == '6', Sccode.use_yn == '1')).all()
    form = superApprovalSearchForm(request.form)

    page = page
    pages = 10
    offset = (pages * (page - 1)) if page != 1 else 0

    if request.method == 'GET':
        applyList = Vcapplymaster.query
        pagination = Pagination(page, pages, applyList.count())
        applyList = applyList.order_by(Vcapplymaster.id.desc()).limit(pages).offset(offset).all()
        log("Transaction").info("[tenant_id:%s][login_id:%s]", ssctenant.tenant_id, current_user.id)

    #supervisory_approve.html 에서 조회조건 쿼리 수행 부분
    if request.method == 'POST':
        vcApplyMasterQuery = Vcapplymaster.query
        visit_category = request.form["visit_category"]
        approval_state = request.form["approval_state"]
        visit_purpose = request.form["visit_purpose"]
        visit_sdate = request.form["visit_sdate"]
        visit_edate = request.form["visit_edate"]
        comp_nm = request.form["comp_nm"]

        #날짜 포맷변경필요 '%m/%d/%Y' to '%y-%m-%d'

        print(request.form)
        if visit_category != "all":
            vcApplyMasterQuery = vcApplyMasterQuery.filter(Vcapplymaster.visit_category == visit_category)

        if approval_state != "all":
            vcApplyMasterQuery = vcApplyMasterQuery.filter(Vcapplymaster.approval_state == approval_state)

        if visit_sdate != "" and visit_edate != "":
            vcApplyMasterQuery = vcApplyMasterQuery.filter(and_(Vcapplymaster.visit_sdate >= visit_sdate, Vcapplymaster.visit_edate <= visit_edate))

        vcApplyMasterQuery = vcApplyMasterQuery.filter(Vcapplymaster.visit_purpose.like("%" + visit_purpose + "%"))
        #                                                  Vcapplymaster.sccompinfo.comp_nm.like("%" + comp_nm + "%"))

        pagination = Pagination(page, pages, vcApplyMasterQuery.count())
        applyList = vcApplyMasterQuery.limit(pages).offset(offset).all()
        log("Transaction").info("[tenant_id:%s][login_id:%s]", ssctenant.tenant_id, current_user.id)

    return render_template(current_app.config['TEMPLATE_THEME'] + '/super_approval/list.html',
                           current_app=current_app,
                           ssctenant=ssctenant,
                           visitCategory = visitCategory,
                           applyList=applyList,
                           pagination=pagination,
                           query_string=request.query_string.decode('utf-8'))


@super_approval.route('/save')
def save():

    return render_template(current_app.config['TEMPLATE_THEME'] + '/super_approval/list.html',
                           current_app=current_app)