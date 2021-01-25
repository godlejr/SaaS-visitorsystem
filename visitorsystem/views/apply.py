from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session, jsonify
from visitorsystem.forms import TestForm

# 2021-01-25, 출입신청화면개발 by hojunghan
apply = Blueprint('apply', __name__)


@apply.route('/', methods=['GET', 'POST'])
def index():
    # print(request.form)
    # form = TestForm(request.form)
    return render_template(current_app.config['TEMPLATE_THEME'] + '/vms_apply/form.html',
                           current_app=current_app,
                         )
