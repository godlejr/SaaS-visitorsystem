"""
gunicorn 실행 모듈

init.py - context processor 포함

"""
import os

from flask import url_for, current_app, request

from visitorsystem import create_app
from visitorsystem.models import Ssctenant

application = create_app(os.getenv('FLASK_CONFIG') or 'default')


@application.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(application.root_path, endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@application.context_processor
def utility_processor():
    def url_for_s3(tenant_id, s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME_VMS'], tenant_id, current_app.config[s3path], filename))

    def get_tenant():
        ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()
        return ssctenant

    return dict(url_for_s3=url_for_s3, get_tenant=get_tenant)


if __name__ == '__main__':
    from flask_script import Manager

    manager = Manager(application)
    manager.run()
