from flask import Blueprint, render_template, current_app

inout_manage = Blueprint('inout_manage', __name__)

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
    Ssctenant, Vcinoutinfo

inout_tag = Blueprint('inout_tag', __name__)


@inout_manage.route('/', methods=['GET', 'POST'], defaults={'page': 1})
@inout_manage.route('/page/<int:page>')
@visit_admin_required
def index(page):
    # visitCategory = db.session.query(Sccode).filter(
    #     and_(Sccode.tenant_id == current_user.ssctenant.id, Sccode.class_id == '6', Sccode.use_yn == '1')).all()
    #
    # today = datetime.datetime.now()
    # end_date = today
    # start_date = today - datetime.timedelta(days=7)
    #
    # searchCondition = {
    #     'admin_sdate': request.args.get('admin_sdate', str(start_date.strftime('%Y-%m-%d'))),
    #     'admin_edate': request.args.get('admin_edate', str(end_date.strftime('%Y-%m-%d'))),
    #     'visit_category': request.args.get('visit_category', 'all'),
    #     'visit_user': request.args.get('visit_user', ''),
    #     'visit_interviewer': request.args.get('visit_interviewer', ''),
    #     'visit_purpose': request.args.get('visit_purpose', ''),
    #     'barcode_state': request.args.get('barcode_state', 'all'),
    #     'comp_nm': request.args.get('comp_nm', ''),
    #     'page': request.args.get('page', page),
    #     'pages': request.args.get('pages', 10)
    # }
    #
    # searchResult = getApplyVisitorListBySearchCondition(searchCondition)
    # log("Transaction").info("[tenant_id:%s][login_id:%s]", current_user.ssctenant.id, current_user.id)

    return render_template(current_app.config['TEMPLATE_THEME'] + '/inout_manage/list.html')


@inout_manage.route('/save/users/<int:user_id>', methods=['GET', 'POST'])
def save(user_id):
    ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()
    applyuser = db.session.query(Vcapplyuser).filter(Vcapplyuser.id == user_id).first()

    today = datetime.datetime.now()
    today_day = str(today.strftime('%Y-%m-%d'))

    barcode = applyuser.barcode
    if barcode is None or barcode == '':
        return jsonify({'msg': '발급이 취소된 QR코드 입니다.'})

    else:
        start_date = applyuser.start_date
        end_date = applyuser.end_date
        if start_date > today_day or end_date < today_day:
            return jsonify({'msg': '방문 기간이 아닙니다. 방문기간 : ' + start_date + ' ~ ' + end_date + ''})

    if db.session.query(Vcinoutinfo).filter(Vcinoutinfo.apply_user_id == user_id,
                                            Vcinoutinfo.in_time >= today_day).first():
        return jsonify({'msg': '이미 방문 확인이 되었습니다.'})

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
