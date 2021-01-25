from flask import Blueprint, render_template, request, current_app
from flask_login import login_required

from visitorsystem.forms import LoginForm
from visitorsystem.models import Ssctenant

main = Blueprint('main', __name__)


@main.context_processor
def utility_processor():
    def url_for_s3(s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))

    return dict(url_for_s3=url_for_s3)



@main.route('/')
#@login_required
def index():

    ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/index.html',current_app=current_app,
                           ssctenant=ssctenant)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    # if request.method == 'POST':
    #     if form.validate():
    #         user = User.query.filter_by(email=form.email.data).first()
    #         if user:
    #             if not check_password_hash(user.password, form.password.data):
    #                 flash('비밀번호가 잘못되었습니다.')
    #             else:
    #                 session['user_id'] = user.id
    #                 session['user_email'] = user.email
    #                 session['user_level'] = user.level
    #                 return redirect(request.args.get("next") or url_for('main.index'))
    #         else:
    #             flash('회원아이디가 잘못되었습니다.')


    ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/login.html', current_app=current_app,
                           ssctenant=ssctenant, form=form)


