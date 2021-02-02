from flask import Blueprint, render_template, request, current_app, flash, session, redirect, url_for
from flask_login import login_required, login_user
from werkzeug.security import check_password_hash

from visitorsystem.forms import LoginForm
from visitorsystem.models import Scuser

main = Blueprint('main', __name__)


@main.route('/')
@login_required
def index():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/index.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate():

            # 사용자 조회
            user = Scuser.query.filter_by(login_id=form.login_id.data).first()

            if user:
                # 비밀번호 비교
                if not check_password_hash(user.login_pwd, form.login_pwd.data):
                    flash('비밀번호가 잘못 되었습니다.')
                else:
                    # 정상 로그인 - 세션
                    session['login_id'] = user.login_id
                    session['name'] = user.name
                    session['auth_id'] = user.auth_id
                    session['tenant_id'] = user.tenant_id
                    login_user(user)
                    return redirect(request.args.get("next") or url_for('main.index'))
            else:
                flash('회원아이디가 잘못되었습니다.')

    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('main.login'))