from flask import Blueprint, render_template, current_app

common_code = Blueprint('common_code', __name__)


@common_code.route('/')
def index():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/common_code/base.html')
