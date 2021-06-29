from flask.blueprints import Blueprint
from .v1 import v1
from .v2 import v2

api = Blueprint('api', __name__)
api.register_blueprint(v2, url_prefix='/v2')
api.register_blueprint(v1, url_prefix='/v1')