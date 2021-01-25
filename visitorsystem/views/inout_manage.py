from flask import Blueprint, render_template, current_app

inout_manage = Blueprint('inout_manage', __name__)


@inout_manage.context_processor
def utility_processor():
    def url_for_s3(s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))

    return dict(url_for_s3=url_for_s3)


@inout_manage.route('/')
def index():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/inout_manage/base.html')


