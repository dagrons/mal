import os
from flask import Flask
import click

from .config import config


def make_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    register_extensions(app)    
    register_blueprints(app)
    register_commands(app)

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

def register_commands(app):
    from .models.feature import Feature
    @app.cli.command("modify_apt")
    @click.argument("task_id")        
    @click.argument("apt_family")
    def modify_apt(task_id, apt_family):        
        if len(Feature.objects(task_id=task_id)) >= 1:
            t = Feature.objects(task_id=task_id).first()        
            t.apt_family = apt_family
            t.save()
            print ("成功更改 {} 的APT家族为 {}".format(task_id, t.apt_family))
        return             


def register_extensions(app):
    from .extensions import mongo
    from .extensions import neo
    mongo.init_app(app)
    neo.init_app(app)