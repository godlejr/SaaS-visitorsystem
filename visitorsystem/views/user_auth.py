from flask import Blueprint, render_template, current_app

user_auth = Blueprint('user_auth', __name__)


@user_auth.route('/')
def index():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/user_auth/base.html')
