"""
gunicorn 실행 모듈

/var/app/inotone/bin/gunicorn manage:app -w 3
"""
import os

from flask import url_for
from visitorsystem import create_app

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


if __name__ == '__main__':
    from flask_script import Manager

    application = Manager(application)
    application.run()
