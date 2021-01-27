from flask import Blueprint, render_template, current_app

inout_tag = Blueprint('inout_tag', __name__)


@inout_tag.route('/')
def index():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/inout_tag/base.html')
