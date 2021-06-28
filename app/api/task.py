from flask import request, jsonify
from . import api
from app.utils import compute_md5
from app.extensions import cuckoo_executor, local_executor


@api.route('/task/create', methods=['POST'])
def create():
    """
    submit a file to cuckoo_executor and local_executor

    :return: the id the task
    """
    upload_file = request.files['file']
    id = compute_md5(upload_file)
    cuckoo_executor.submit(id, upload_file)
    local_executor.submit(id, upload_file)
    return {'id': id}


@api.route('/task/status/<id>', methods=['GET'])
def status(id):
    """
    check the status of a uploaded task

    :return: the status of task in cuckoo executor and local executor
    """
    rcuckoo = cuckoo_executor.status(id)
    rlocal = local_executor.status(id)
    return jsonify({
        "cuckoo": rcuckoo,
        "local": rlocal
    })


@api.route('/task/result/<id>', methods=['GET'])
def result(id):
    """
    return the result of task

    :return: 
    """
    rcuckoo = cuckoo_executor.status(id)
    rlocal = local_executor.status(id)
    if rcuckoo == "done" and rlocal == "done":
        return jsonify({
            "cuckoo": cuckoo_executor.result(id),
            "local": local_executor.result(id)
        })
    else:
        return jsonify({
            "warning": "task still running, returned status as alternative",
            "cuckoo": cuckoo_executor.status(id),
            "local": local_executor.status(id)
        })
