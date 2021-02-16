from flask import Blueprint, render_template, current_app, request, jsonify
from flask_login import current_user

from visitorsystem.models import db, Scclass, Sccode
from loggers import log

common_code = Blueprint('common_code', __name__)


@common_code.route('/')
def index():
    tenant_id = current_user.ssctenant.id
    scClasses = db.session.query(Scclass).filter(Scclass.use_yn == '1',
                                                 Scclass.user_def_yn == 'Y', Scclass.class_nm != '정문',
                                                 Scclass.class_nm != '사업장').all()

    scCodeObject = db.session.query(Sccode).filter(Sccode.tenant_id == tenant_id, Sccode.use_yn == '1')

    # 사업장
    sites = scCodeObject.filter(Sccode.class_nm == '사업장').order_by(Sccode.class_nm).all()

    # 정문
    gates = scCodeObject.filter(Sccode.class_nm == '정문').order_by(Sccode.class_nm).all()

    # 나머지 코드
    codes = scCodeObject.filter(Sccode.class_nm != '정문', Sccode.class_nm != '사업장').order_by(Sccode.class_nm).all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/system/common_code/list.html',
                           current_app=current_app
                           , scClasses=scClasses, sites=sites, gates=gates, codes=codes)


@common_code.route('/<type>/save', methods=['POST'])
def save(type):
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id

        code_name = request.form[type + '_name']
        if code_name.strip() == '':
            return jsonify({'msg': '공백 입니다.'})

        if type == 'site':
            class_name = "사업장"
        elif type == 'gate':
            if request.form['site_type'] == '':
                return jsonify({'msg': '사업장을 선택하세요.'})
            class_name = "정문"

        elif type == 'code':
            if request.form[type + '_type'] == '':
                return jsonify({'msg': '속성을 선택하세요.'})

            class_name = request.form[type + '_type']

        result = db.session.query(Sccode).filter(Sccode.tenant_id == tenant_id, Sccode.code_nm == code_name,
                                                 Sccode.class_nm == class_name, Sccode.use_yn == '1').first()

        scClass = db.session.query(Scclass).filter(Scclass.use_yn == '1', Scclass.class_nm == class_name,
                                                   Scclass.user_def_yn == 'Y').first()

        if not result:
            # 최근 추가 코드(코드 별 내림차순)
            recentCode = db.session.query(Sccode).filter(Sccode.tenant_id == tenant_id,
                                                         Sccode.class_nm == class_name, Sccode.use_yn == '1').order_by(
                Sccode.code.desc()).all()
            newCode = str(int(recentCode[0].code) + 10)  # 코드 + 50

            siteCodeforGate = ''
            if type == 'gate':
                # site for Gate
                site_code_name = request.form['site_type']
                siteCode = db.session.query(Sccode).filter(Sccode.tenant_id == tenant_id,
                                                           Sccode.code_nm == site_code_name,
                                                           Sccode.class_nm == '사업장', Sccode.use_yn == '1').first()
                siteCodeforGate = siteCode.code

            # 신규 코드 작성
            sccode = Sccode()
            sccode.scclass = scClass  # 클래스 추가
            sccode.class_nm = class_name  # class 이름 - 사업장 / 정문
            sccode.tenant_id = tenant_id  # 테넌트 ID

            sccode.attb_a = siteCodeforGate

            sccode.code = newCode  # 코드 추가
            sccode.code_nm = code_name

            db.session.add(sccode)
            db.session.commit()

        else:
            return jsonify({'msg': '이미 있는 ' + class_name + ' 입니다.'})

        return jsonify({'msg': class_name + '이(가) 추가 되었습니다.'})

#
# @common_code.route('/{type}/edit', methods=['POST'])
# def edit(type):
#     if request.method == 'POST':
#         tenant_id = current_user.ssctenant.id
#         id = int(request.form['id'])
#
#         for row in db.session.query(Scrule).filter(Scrule.tenant_id == tenant_id, Scrule.id == id).all():
#             scrule = {
#                 "rule_name": row.rule_name,
#                 "rule_type": row.rule_type,
#                 "rule_duedate": row.rule_duedate,
#                 "rule_desc": row.rule_desc
#             }
#     return jsonify({'msg': scrule})
#
#
# @common_code.route('/{type}/delete', methods=['POST'])
# def delete(type):
#     if request.method == 'POST':
#         tenant_id = current_user.ssctenant.id
#         id = int(request.form['id'])
#         scrule = db.session.query(Scrule).filter(Scrule.tenant_id == tenant_id, Scrule.id == id).first()
#         scrule.use_yn = '0'
#         db.session.commit()
#         return jsonify({'msg': 'success'});
