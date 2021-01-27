from flask import Blueprint, render_template, current_app

super_approval = Blueprint('super_approval', __name__)


@super_approval.route('/')
def index():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/super_approval/base.html')
