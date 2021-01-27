from flask import Blueprint, render_template, current_app

inout_apply = Blueprint('inout_apply', __name__)


@inout_apply.route('/')
def index():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/inout_apply/base.html')


