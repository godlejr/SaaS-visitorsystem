from flask import Blueprint, render_template, current_app

common_code = Blueprint('common_code', __name__)


@common_code.context_processor
def utility_processor():
    def url_for_s3(s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))

    return dict(url_for_s3=url_for_s3)


@common_code.route('/')
def index():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/common_code/base.html')


