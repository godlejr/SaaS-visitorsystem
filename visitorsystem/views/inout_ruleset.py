from flask import Blueprint, render_template, current_app

inout_ruleset = Blueprint('inout_ruleset', __name__)


@inout_ruleset.route('/')
def index():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/inout_ruleset/base.html')
