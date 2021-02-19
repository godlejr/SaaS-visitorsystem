from flask import Blueprint, render_template, current_app
from flask_login import current_user

user_auth = Blueprint('user_auth', __name__)


@user_auth.route('/')
def index():

    print(current_user.get_auth.code_nm)

    return render_template(current_app.config['TEMPLATE_THEME'] + '/user_auth/base.html')
