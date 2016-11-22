import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SSL_DISABLE = True  # FIXME
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # FIXME
    SQLALCHEMY_RECORD_QUERIES = True  # FIXME

    @staticmethod
    def init_app(app):
        pass


class TestingConfig(Config):
    WTF_CSRF_ENABLED = False   # FIXME
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or\
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or\
                              'postgresql+psycopg2://test:test@localhost:5432/instabattle_test'


config = {
    'testing': TestingConfig
}
