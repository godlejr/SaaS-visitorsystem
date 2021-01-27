from flask import Blueprint, render_template, current_app

user_account = Blueprint('user_account', __name__)


@user_account.route('/')
def index():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/user_account/base.html')
