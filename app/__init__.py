import os
from flask import Flask
from .config import config


def make_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    register_extensions(app)    
    register_blueprints(app)

    return app


def register_blueprints(app):
    from .services import TaskExecutor, FeatureService
    from .main import main
    from .api import api    
    from .api.v2.task import TaskAPI
    from .api.v2.feature import FeatureAPI    
    with app.app_context():
        """
        DI
        """
        task_executor = TaskExecutor()
        feature_service = FeatureService(task_executor)
        TaskAPI(task_executor, feature_service)
        FeatureAPI(task_executor, feature_service)
    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(api, url_prefix='/api')


def register_extensions(app):
    from .extensions import mongo
    from .extensions import neo
    mongo.init_app(app)
    neo.init_app(app)
