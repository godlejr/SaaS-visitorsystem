import os

class Config(object):
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False
    CSRF_ENABLED = True
    SECRET_KEY = 'secret'
    TEMPLATE_THEME = 'bootstrap'
    NO_IMG = 'noimg.JPG'

    #권한
    AUTH_ADMIN = '9990'
    AUTH_VISIT_ADMIN = '3000'
    AUTH_VISITOR = '1000'
    AUTH_APPROVAL = '2000'

    #코로나 공공데이터 키
    COVID_SECURITY_KEY = '5%2FCy2c2pZ4DIwEYhfel4ZahBvrStmGZiu%2BGUkXLq2YwUdNDt%2FZLzLoRhzGAd9DtKi2Jhq%2Bg9WriseQNNPgsTbg%3D%3D'
    COVID_SERVICE_URL = ' http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson'

    #개발
    #REDIS_URL = 'redis://127.0.0.1:6379/0'

    #운영
    REDIS_URL = 'redis://vms-redis-prod.wv2xup.ng.0001.apn2.cache.amazonaws.com:6379/0'

    S3_BUCKET_NAME = 'http://static.inotone.co.kr'
    S3_IMG_DIRECTORY = '/data/img/'
    S3_USER_DIRECTORY = '/data/user/'
    S3_COVER_DIRECTORY = '/data/cover/'
    UPLOAD_TMP_DIRECTORY = '/tmp/'
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    #S3 VMS
    # 개발
    S3_BUCKET_NAME_VMS = 'https://vms-tenants-bucket-dev.s3.ap-northeast-2.amazonaws.com/'

    #운영
    #S3_BUCKET_NAME_VMS = 'https://vms-tenants-bucket.s3.ap-northeast-2.amazonaws.com/'


    S3_IMG_DIRECTORY_VMS = '/data/img/'  # 공통 Config
    S3_IMG_MAIN_DIRECTORY_VMS = '/data/img/main/'  # 메인이미지
    S3_IMG_MAIN_LOGO_DIRECTORY_VMS = '/data/img/main/logo/'  # 회사이미지

    S3_IMG_MAIN_BANNER_DIRECTORY_VMS = '/data/img/main/banner/' # 배너 이미지 (banner1.jpg / banner2.jpg / banner3.jpg )

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'dev@inotone.co.kr'
    MAIL_PASSWORD = 'xxxxxxxx'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    YOUTUBE_API_SCOPES = ['https://www.googleapis.com/auth/youtube']
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 10
    SQLALCHEMY_POOL_RECYCLE = 1800
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #운영
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:xxxxxxxxx!@vms-database.cluster-cseigyxe813j.ap-northeast-2.rds.amazonaws.com/vmswebprod'

    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://saas:xxxxxxxxx@172.19.116.78:3307/hccwebdev'
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://saas:xxxxxxxxx@localhost:3306/hccwebdev'
    SOCIAL_FACEBOOK = {
        'consumer_key': 'xxxxxxxx',
        'consumer_secret': 'xxxxxxxxx'
    }


    #S3 Upload Key
    AWS_ACCESS_KEY = "xxxxxxxxx"
    AWS_SECRET_KEY = "xxxxxxxxx"
    BUCKET_NAME = "vms-tenants-bucket-dev"

    #SNS Key

    AWS_SNS_ACCESS_KEY = "xxxxxxxxx"
    AWS_SNS_SECRET_KEY = "xxxxxxxxx"
    AWS_SNS_REGION_NAME = "ap-northeast-1"
    AWS_SNS_SMS_TOPIC_ARN = "arn:aws:sns:ap-northeast-1:305217637296:VMS_SMS"



class ProductionConfig(Config):
    DEBUG = False
    #개발
    #REDIS_URL = '127.0.0.1'

    #운영
    REDIS_URL = 'redis://vms-redis-prod.wv2xup.ng.0001.apn2.cache.amazonaws.com:6379'
    TEMPLATE_THEME = 'bootstrap'
    SECRET_KEY = os.getenv('SECRET_KEY') or 'xxxxxxxxxx'


class StagingConfig(Config):
    DEBUG = True

class DevelopmentConfig(Config):
    DEBUG = False
    DEVELOPMENT = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class TestingConfig(Config):
    TESTING = False


def init_app(app, config_name):
    app.config.from_object({
        'testing': TestingConfig,
        'production': ProductionConfig,
        'development': DevelopmentConfig,
        'default': DevelopmentConfig
    }[config_name]())
