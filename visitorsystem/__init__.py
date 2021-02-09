import os

from flask import Flask, render_template, session
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from redis import Redis
from werkzeug.utils import redirect

import config
from visitorsystem.lib.redis_session import RedisSessionInterface
from visitorsystem.models import db, File, Photo, Magazine, MagazineComment, PhotoComment, Comment, Board, \
    Category, \
    Residence, Scuser

# from visitorsystem.views import mail

def create_app(config_name):
    """
    :return: Flask App

    Flask App 생성
    """
    current_dir = os.path.abspath(os.path.dirname(__file__))
    template_folder = os.path.join(current_dir, 'templates')

    application = Flask(__name__, template_folder=template_folder)
    application.jinja_env.auto_reload = True
    application.jinja_env.autoescape = False
    application.jinja_env.add_extension('jinja2.ext.loopcontrols')

    config.init_app(application, config_name)
    db.init_app(application)
    # mail.init_app(application)

    redis = Redis.from_url(application.config['REDIS_URL'])
    application.redis = redis
    application.session_interface = RedisSessionInterface(redis)

    toolbar = DebugToolbarExtension()
    toolbar.init_app(application)

    # admin example
    # admin = Admin(application, name='Happy@Home', template_mode='bootstrap3', index_view=MyAdminIndexView())
    # admin.add_view(UserAdmin(User, db.session, name='사용자관리', endpoint='user'))
    # admin.add_view(ClassAdminCategory(Category, db.session, name='테마', category='분류 관리', endpoint='category'))
    # admin.add_view(ClassAdminResidence(Residence, db.session, name='장소', category='분류 관리', endpoint='residence'))
    # admin.add_view(ClassAdminBusiness(Business, db.session, name='업종', category='분류 관리', endpoint='business'))
    # admin.add_view(ClassAdminPhoto(Photo, db.session, name='포토', category='컨텐츠 관리', endpoint='photo'))
    # admin.add_view(ClassAdminMagazine(Magazine, db.session, name='매거진', category='컨텐츠 관리', endpoint='magazine'))
    # admin.add_view(CommentAdminFile(Comment, db.session, name='댓글', category='댓글 관리', endpoint='comment'))
    # admin.add_view(BoardAdminFile(Board, db.session, name='해피QnA', category='댓글 관리',endpoint='board'))

    # Application Blueprints (내방객 시스템)
    from visitorsystem.views.main import main as main_blueprint
    from visitorsystem.views.user_account import user_account as user_account_blueprint
    from visitorsystem.views.user_auth import user_auth as user_auth_blueprint
    from visitorsystem.views.super_approval import super_approval as super_approval_blueprint
    from visitorsystem.views.common_code import common_code as common_code_blueprint
    from visitorsystem.views.inout_apply import inout_apply as inout_apply_blueprint
    from visitorsystem.views.inout_manage import inout_manage as inout_manage_blueprint
    from visitorsystem.views.inout_ruleset import inout_ruleset as inout_ruleset_blueprint
    from visitorsystem.views.inout_tag import inout_tag as inout_tag_blueprint
    from visitorsystem.views.statistics import statistics as statistics_blueprint

    application.register_blueprint(main_blueprint)
    application.register_blueprint(user_account_blueprint, url_prefix='/userAccount')
    application.register_blueprint(user_auth_blueprint, url_prefix='/userAuth')
    application.register_blueprint(super_approval_blueprint, url_prefix='/superApproval')
    application.register_blueprint(common_code_blueprint, url_prefix='/commonCode')
    application.register_blueprint(inout_apply_blueprint, url_prefix='/inoutApply')
    application.register_blueprint(inout_manage_blueprint, url_prefix='/inoutManage')
    application.register_blueprint(inout_ruleset_blueprint, url_prefix='/inoutRuleset')
    application.register_blueprint(inout_tag_blueprint, url_prefix='/inoutTag')
    application.register_blueprint(statistics_blueprint, url_prefix='/statistics')

    from visitorsystem.views.example.test import test as test_blueprint
    application.register_blueprint(test_blueprint, url_prefix='/test')

    application.errorhandler(403)(lambda e: redirect('/'))
    application.errorhandler(404)(lambda e: render_template('error/404.html'))
    application.errorhandler(500)(lambda e: render_template('error/404.html'))

    # log = ('Redis')
    # handler = logging.StreamHandler(sys.stderr)
    # handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
    # log.addHandler(handler)
    # log.setLevel(logging.INFO)

    login_manager = LoginManager()
    login_manager.init_app(application)
    login_manager.login_view = 'main.login'
    login_manager.login_message = '로그인 후 이용해주세요.'

    from loggers import loggerSet
    loggerSet()

    @login_manager.user_loader
    def load_user(login_id):
        # print(session['id'])
        return Scuser.query.filter_by(id=session['id']).first()

    return application

