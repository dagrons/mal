from flask.json import jsonify
from . import api
from app.extensions import cuckoo_executor, local_executor


@api.route('/feature/get/<id>')
def get(id):
    return jsonify({
        'cuckoo': cuckoo_executor.result(id),
        'local': local_executor.result(id)
    })
