from flask import Blueprint, render_template, current_app, request, url_for, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.utils import redirect

from visitorsystem.forms import UserAccountFrom
from visitorsystem.models import db, Vcapplymaster, Scuser

user_account = Blueprint('user_account', __name__)

@user_account.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print('호출')
        return redirect(url_for('user_account.index'))

    return render_template(current_app.config['TEMPLATE_THEME'] + '/system/user_account/list.html')


@user_account.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':

        #비밀번호와 비밀번호 확인이 동일하면 수정

        #사용자의 데이터를 업데이트,
        updateUser = Scuser(current_app.user.id)

        updateUser.name = request.form['name']  # 이름
        updateUser.login_id = request.form['login_id']  # 로그인 id
        updateUser.login_pwd = generate_password_hash(request.form['login_pwd'])  # 로그인 pwd , sha256 암호화
        updateUser.biz_no = request.form['biz_no']  # biz_no
        updateUser.comp_nm = request.form['comp_nm']  # 회사명
        updateUser.phone = request.form['phone']  # 핸드폰
        updateUser.email = request.form['email']  # 이메일

        db.session.add(updateUser)
        db.session.commit()

        # applyform = UserAccountFrom(request.form)
        # apply = Vcapplymaster()
        # apply.apply_code ='APPLY-002'
        # apply.apply_nm = '방문신청 2번'
        # apply.interviewr = request.form['interviewer_name']  # 감독자
        # apply.applicant = request.form['applicant_name'] # 신청자
        # apply.phone = request.form['applicant_phone'] # 감독자 휴대폰
        # apply.visit_category = request.form['inout_purpose_type'] # 방문종류
        # apply.biz_no = request.form['inout_biz_no'] # 사업자번호
        # apply.visit_sdate = request.form['inout_sdate'] # 방문시작일
        # apply.visit_edate = request.form['inout_edate'] # 방문종료일
        # apply.visit_purpose = request.form['inout_title'] # 방문목적
        # apply.visit_desc = request.form['inout_purpose_desc']#방문목적 상세기술
        # apply.site_id = 'U1'  # 사업장코드
        # apply.site_nm = '울산1공장' # 사업장명
        # # apply.site_id = request.form['inout_location'].data #
        # # apply.site_nm = request.form['inout_location_desc'].data
        # apply.login_id = 'admin' #로그인 아이디(세션에서 가져오기)
        # apply.approval_state = '대기' #방문승인 상태 저장
        # db.session.add(apply)
        # db.session.commit()

    return jsonify({'file_name': 'output'})
