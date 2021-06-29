from flask import Blueprint
from .task import task_bp
from .feature import feature_bp

v1 = Blueprint('v1', __name__)
v1.register_blueprint(task_bp, url_prefix='/tasks')
v1.register_blueprint(feature_bp, url_prefix='/feature')
