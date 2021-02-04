from flask import Blueprint, render_template, current_app

statistics = Blueprint('statistics', __name__)


@statistics.route('/')
def index():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/statistics/base.html')
