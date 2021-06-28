from flask import json, abort, send_file
from flask.json import jsonify
from . import api
from app.extensions import cuckoo, cuckoo_executor, local_executor
from app.models.local import Local


@api.route('/feature/report/get/<id>')
def get_report(id):
    """
    get the report of a finished task, the task must be finished

    :param id: task id
    """
    return jsonify({
        'cuckoo': cuckoo_executor.result(id),
        'local': local_executor.result(id)
    })
    
@api.route('/feature/bmp/get/<filename>')
def get_png(id):
    """
    get the greyscale image of a malware

    :param id: task id
    """
    if len(Local.objects(task_id=id)) < 1:
        abort(404)
    return send_file(Local.objects(task_id=id).first().local.bmp_file, attachment_filename=id+'.bmp')