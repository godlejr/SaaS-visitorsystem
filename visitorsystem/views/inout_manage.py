from flask import Blueprint, render_template, current_app

inout_manage = Blueprint('inout_manage', __name__)


@inout_manage.route('/')
def index():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/inout_manage/base.html')
