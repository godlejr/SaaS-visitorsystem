from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session, jsonify
from visitorsystem.forms import TestForm
test = Blueprint('test', __name__)

"""
BLUEPRINT
1.블루프린트 만들기
첫번째 인자(블루프린트이름)

2.main.py에 등록(우리 프로젝트에서는 __init_.py에 등록하면됨)
-from visitorsystem.views.test import test as test_blueprint
 application.register_blueprint(test_blueprint, url_prefix='/test')
 
3.데코레이터 명도 @test로 시작해야한다.
"""


@test.route('/', methods=['GET', 'POST'])
def index():
    print(request.form)
    form = TestForm(request.form)
    return render_template(current_app.config['TEMPLATE_THEME'] + '/test/form.html',
                           current_app=current_app,
                           form=form)
#
# @main.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm(request.form)
#     if request.method == 'POST':
#         if form.validate():
#             user = User.query.filter_by(email=form.email.data).first()
#             if user:
#                 if not check_password_hash(user.password, form.password.data):
#                     flash('비밀번호가 잘못되었습니다.')
#                 else:
#                     session['user_id'] = user.id
#                     session['user_email'] = user.email
#                     session['user_level'] = user.level
#                     return redirect(request.args.get("next") or url_for('main.index'))
#             else:
#                 flash('회원아이디가 잘못되었습니다.')
#
#     # print('-------------------')
#     # print(Ssctenant.query)
#     # print('-------------------')
#     # ssctenants = Ssctenant.query.all()
#     return render_template(current_app.config['TEMPLATE_THEME'] + '/main/login.html', form=form)