from flask import json, abort, send_file
from flask.json import jsonify
from . import v2


class FeatureAPI():
    def __init__(self, task_executor, feature_service):
        self.task_executor = task_executor
        self.feature_service = feature_service
        v2.add_url_rule('/feature/dashboard', view_func=self.dashboard)
        v2.add_url_rule('/feature/bmp/get/<filename>', view_func=self.get_png)
        v2.add_url_rule('/feature/report/get/<id>', view_func=self.get_report)

    def dashboard(self):
        """
        infos about the database and running tasks
        """
        return jsonify(self.feature_service.dashboard())

    def get_png(self, filename):
        """
        return png of malware

        :param filename: task id
        """
        if self.feature_service.get_png(filename) == None:
            abort(404)
        else:
            return send_file(self.feature_service.get_png(filename), attachment_filename=filename+'.bmp')

    def get_report(self, id):
        """
        return report of a task if reported, 
        if in queue, return status of the task,
        else return error

        :param id: task id
        :return: status of the task | report | error
        """
        res = self.task_executor.status(id)
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
            report = self.feature_service.get_report(id)
            five_most_like = self.feature_service.top_5_similar(
                report.local.malware_sim_doc2vec)
            return jsonify({
                'status': 'reported',
                'msg': 'reported',
                'isvalid': True,
                'report': report,
                'five_most_like': five_most_like
            })
