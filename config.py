import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SSL_DISABLE = True  # FIXME
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # FIXME
    SQLALCHEMY_RECORD_QUERIES = True  # FIXME

    @staticmethod
    def init_app(app):
        pass


class TestingConfig(Config):
    WTF_CSRF_ENABLED = False   # FIXME
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or\
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or\
                              'postgresql+psycopg2://test:test@localhost:5432/instabattle_test'


class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

config = {
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig
}
