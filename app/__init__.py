from config import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    # List of blueprints FIXME
    # from .main import main as main_blueprint
    # app.register_blueprint(main_blueprint)
    from .api import create_blueprint as create_api_blueprint
    app.register_blueprint(create_api_blueprint())

    return app
