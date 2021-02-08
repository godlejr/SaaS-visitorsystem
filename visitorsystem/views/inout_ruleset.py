from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify, flash
from flask_login import current_user

from visitorsystem.models import db, Scrule, Ssctenant

inout_ruleset = Blueprint('inout_ruleset', __name__)


@inout_ruleset.route('/', methods=['GET'])
def index():
    tenant_id = current_user.ssctenant.id
    scrules = db.session.query(Scrule).filter(Scrule.tenant_id == tenant_id, Scrule.use_yn == '1').all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/inout_ruleset/list.html'
                           , current_app=current_app
                           , scrules=scrules)

@inout_ruleset.route('/save', methods=['POST'])
def save():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id
        rule_name = request.form['rule_name']
        result = db.session.query(Scrule).filter(Scrule.tenant_id == tenant_id, Scrule.rule_name == rule_name).all()

        if not result:
            scrule = Scrule()
            scrule.tenant_id = tenant_id  # 테넌트ID
            scrule.rule_name = request.form['rule_name']  # 규칙이름
            scrule.rule_type = request.form['rule_type']  # 규칙유형
            scrule.rule_duedate = request.form['rule_duedate']  # 규칙기간
            scrule.rule_desc = request.form['rule_desc']  # 규칙설명
            scrule.rule_tlocation = request.form['rule_name']  # text정보 location
            db.session.add(scrule)
            db.session.commit()
        else:
            db.session.query(Scrule) \
                .filter(Scrule.tenant_id == tenant_id, Scrule.rule_name == rule_name) \
                .update({
                'rule_type': request.form['rule_type'],
                'rule_duedate': request.form['rule_duedate'],
                'rule_desc': request.form['rule_desc'],
            })
            db.session.commit()

        return jsonify({'msg': '규칙이 성공적으로 저장되었습니다.'})


@inout_ruleset.route('/edit', methods=['POST'])
def edit():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id
        id = int(request.form['id'])

        for row in db.session.query(Scrule).filter(Scrule.tenant_id == tenant_id, Scrule.id == id).all():
            scrule = {
                "rule_name": row.rule_name,
                "rule_type": row.rule_type,
                "rule_duedate": row.rule_duedate,
                "rule_desc": row.rule_desc
            }
    return jsonify({'msg': scrule})


@inout_ruleset.route('/delete', methods=['POST'])
def delete():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id
        id = int(request.form['id'])
        scrule = db.session.query(Scrule).filter(Scrule.tenant_id == tenant_id, Scrule.id == id).first()
        scrule.use_yn = '0'
        db.session.commit()
        return jsonify({'msg': 'success'});
