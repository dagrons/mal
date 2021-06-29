from flask import Blueprint

v2 = Blueprint('v2', __name__)

from . import task, feature

