from app.services import feature_service
from flask import json, request, jsonify
from . import v2
from app.utils.compute_md5 import compute_md5
from app.utils.is_pe import is_pe
from app.services import task_executor, feature_service


@v2.route('/tasks/create', methods=['POST'])  # v1 adaptable
@v2.route('/task/create', methods=['POST'])
def create():
    """
    submit a new task
    """
    upload_file = request.files['file']
    id = compute_md5(upload_file)

    if not is_pe(upload_file):
        return jsonify({
            'status': 'error',
            'msg': 'is not a pe file!',
            'filename': id
        })
    elif task_executor.status(id) in ('running', 'done', 'reported'):
        return jsonify({
            'status': 'success',
            'msg': 'task finished',
            'filename': id
        })
    else:
        task_executor.submit(id, upload_file)
        return jsonify({
            'status': 'success',
            'msg': 'task appended to the queue',
            'filename': id
        })


@v2.route('/tasks/query/cnt')  # v1 adaptable
@v2.route('/task/left_cnt')
def left_cnt():
    """
    how many task running currently    
    """
    return str(task_executor.left_cnt())
