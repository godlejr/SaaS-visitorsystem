from operator import and_

from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify
from flask_login import current_user, login_required
from visitorsystem.forms import ApplyForm
from visitorsystem.models import db, Vcapplymaster, Ssctenant, Scrule, Vcvisituser
from datetime import datetime
import time

inout_apply = Blueprint('inout_apply', __name__)




@inout_apply.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        # print('============================')
        # print(applyform.stringfield.data)
        # print(applyform.textAreaField.data)
        # print(applyform.validate())
        #
        # flash("잘못된 로그인")
        # print('============================')
        return redirect(url_for('inout_apply.index'))
    else:
        return render_template(current_app.config['TEMPLATE_THEME'] + '/inout_apply/section4.html')


@inout_apply.route('/create', methods=['POST'])
def create():
    if request.method == 'POST':
        applyform = ApplyForm(request.form)
        apply = Vcapplymaster()
        apply.apply_code = 'APPLY-002'
        apply.apply_nm = '출입신청 2번'
        apply.interviewr = request.form['interviewer_name']  # 감독자
        apply.applicant = request.form['applicant_name']  # 신청자
        apply.phone = request.form['applicant_phone']  # 감독자 휴대폰
        apply.visit_category = request.form['inout_purpose_type']  # 방문종류
        apply.biz_no = request.form['inout_biz_no']  # 사업자번호
        apply.visit_sdate = request.form['inout_sdate']  # 방문시작일
        apply.visit_edate = request.form['inout_edate']  # 방문종료일
        apply.visit_purpose = request.form['inout_title']  # 방문목적
        apply.visit_desc = request.form['inout_purpose_desc']  # 방문목적 상세기술
        apply.site_id = 'U1'  # 사업장코드
        apply.site_nm = '울산1공장'  # 사업장명
        # apply.site_id = request.form['inout_location'].data #
        # apply.site_nm = request.form['inout_location_desc'].data
        apply.login_id = 'admin'  # 로그인 아이디(세션에서 가져오기)
        apply.approval_state = '대기'  # 출입승인 상태 저장
        db.session.add(apply)
        db.session.commit()

    return jsonify({'file_name': 'output'})


"""
감독자 조회로직
001.SC_USER 테이블에서, name 필드로 조회
002.조회 후, return 값은 json 형식으로 반환
003. 표 binding 후 보여주기
"""


@inout_apply.route('/rule/search', methods=['POST'])
def ruleSearch():

    ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()
    tenant_id = ssctenant.tenant_id

    lists = []
    for row in db.session.query(Scrule).filter(Scrule.tenant_id == tenant_id).all():
        dict = {
            "rule_name": row.rule_name,
            "rule_type": row.rule_type,
            "rule_duedate": row.rule_duedate,
            "rule_desc": row.rule_desc
        }
        lists.append(dict)

    return jsonify({'msg': lists})

"""
Rule 유효성 판별
"""
@inout_apply.route('/rule/valid', methods=['POST'])
def ruleValidate():
    ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()
    tenant_id = ssctenant.tenant_id
    print(request.form)

    vsdate = request.form['sdate'] #방문시작 날짜
    # vsdate = time.mktime(datetime.strptime(vsdate,'%Y-%m-%d').timetuple())

    vedate = request.form['edate'] #방문종료 날짜
    # vedate = time.mktime(datetime.strptime(vedate, '%Y-%m-%d').timetuple())

    name = request.form['userName'] #사용자 이름
    phone = request.form['userPhone'] #휴대폰 번호

    ruleList = []
    lists = []
    dict = {}

    #1.현재 등록된 모든 Rule을 모두 가져온다.
    for row in db.session.query(Scrule).all():
        ruleList.append(row.rule_name)
        dict[row.rule_name] = False


    # 2.tenant에 등록된 RULE을 기준으로, name/phone/유효일자를 검색하는 로직, 규칙시작일(s_date) <=방문시작일(vsdate) / 규칙종료일(e_date) >=방문종료일(vedate)
    for rule_name in ruleList :
        for row in db.session.query(Vcvisituser)\
                .filter(Vcvisituser.name == name, Vcvisituser.phone == phone,
                        Vcvisituser.rule_name == rule_name,
                        and_(Vcvisituser.s_date <= vsdate,Vcvisituser.e_date >= vedate)):
           dict[row.rule_name] = True
           lists.append(dict)


    print(lists)


    return jsonify({'msg': '와웅'})


@inout_apply.route('/interview/search', methods=['POST'])
def interviewSearch():
    if request.method == 'POST':
        interviewName = request.form['interviewName'];
        data = '{"name": "Book1", "ISBN": "12345", "author": [{"name": "autho1", "age": 30}, {"name": "autho2", "age": 25}]}'
        return jsonify({'file_name': 'output'});

# print('============================')
# print(applyform.stringfield.data)
# print(applyform.textAreaField.data)
# print(applyform.validate())
#
# flash("잘못된 로그인")
# print('============================')
# return redirect(url_for('inout_apply.index'))

# class superApprovalSearchForm(Form):
# # validators=[DataRequired()] : 필수 입력 값
# # 날짜 유효성 검사 부분 추가 필요
# # visit_sdate = DateField('시작일')
# # visit_edate = DateField('종료일')
# visit_sdate = StringField('시작일',validators=[DataRequired()])
# visit_edate = StringField('종료일',validators=[DataRequired()])
# visit_category = StringField('방문구분')
# apply_nm = StringField('작업명')
# comp_nm = StringField('업체명')
# approval_state = StringField('진행상태')
