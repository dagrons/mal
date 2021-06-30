import os
from flask import Flask
from .config import config
from .extensions import mongo
from .main import main
from .api import api
from .service import local_executor, cuckoo_executor
from .extensions import neo


def make_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)    

    init_service(app)

    return app


def register_blueprints(app):
    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(api, url_prefix='/api')


def register_extensions(app):
    mongo.init_app(app)
    neo.init_app(app)

def init_service(app):
    with app.app_context():
        local_executor.init_service()
        cuckoo_executor.init_service()