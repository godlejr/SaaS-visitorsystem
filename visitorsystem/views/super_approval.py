from flask import Blueprint, render_template, current_app

super_approval = Blueprint('super_approval', __name__)


@super_approval.context_processor
def utility_processor():
    def url_for_s3(s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))

    return dict(url_for_s3=url_for_s3)


@super_approval.route('/')
def index():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/super_approval/base.html')


