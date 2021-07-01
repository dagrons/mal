from app.api.v1 import feature
from re import L
from flask import json, abort, send_file
from flask.json import jsonify

from . import v2
from app.services import task_executor, feature_service


@v2.route('/feature/dashboard')
def dashboard():
    """
    infos about the database and running tasks
    """
    return jsonify(feature_service.dashboard())


@v2.route('/feature/bmp/get/<filename>')
def get_png(filename):
    """
    return png of malware

    :param filename: task id
    """
    if feature_service.get_png(filename) == None:
        abort(404)
    else:
        return send_file(feature_service.get_png(filename), attachment_filename=filename+'.bmp')


@v2.route('/feature/report/get/<id>')
def get_report(id):
    """
    return report of a task if reported, 
    if in queue, return status of the task,
    else return error

    :param id: task id
    :return: status of the task | report | error
    """
    res = task_executor.status(id)
    if res == "empty" or res == "exception":
        return jsonify({
            'status': 'error',
            'msg': 'the report do not exist or task meet an exception',
            'isvalid': False
        })
    elif res == "running" or res == "done":
        # if done but not reported, can be considered as running
        return jsonify({
            'status': 'running',
            'msg': 'the task is still running',
            'isvalid': True,
        })
    else:
        report = feature_service.get_report(id)
        five_most_like = feature_service.top_5_similar(
            report.local.malware_sim_doc2vec)
        return jsonify({
            'status': 'reported',
            'msg': 'reported',
            'isvalid': True,
            'report': report,
            'five_most_like': five_most_like
        })
