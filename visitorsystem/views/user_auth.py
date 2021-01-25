from flask import Blueprint, render_template, current_app

user_auth = Blueprint('user_auth', __name__)


@user_auth.context_processor
def utility_processor():
    def url_for_s3(s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))

    return dict(url_for_s3=url_for_s3)


@user_auth.route('/')
def index():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/user_auth/base.html')


