import tempfile
from flask import json, request, jsonify
from . import v2
from app.utils.compute_md5 import compute_md5
from app.utils.is_pe import is_pe


class TaskAPI():
    def __init__(self, task_executor, feature_service):
        self.task_executor = task_executor
        self.feature_service = feature_service
        v2.add_url_rule('/tasks/create',
                        methods=['POST'], view_func=self.create)
        v2.add_url_rule(
            '/task/create', methods=['POST'], view_func=self.create)
        v2.add_url_rule('/tasks/query/cnt', view_func=self.left_cnt)
        v2.add_url_rule('/task/left_cnt', view_func=self.left_cnt)
        v2.add_url_rule('/task/status/<id>', view_func=self.status)
        v2.add_url_rule('/task/running_list', view_func=self.running_list)
        v2.add_url_rule('/task/pending_list', view_func=self.pending_list)
        v2.add_url_rule('/task/pending_cnt', view_func=self.pending_cnt)        

    def create(self):
        """
        submit a new task
        """
        upload_file = request.files['file']

        id = compute_md5(upload_file)
        u, upath = tempfile.mkstemp()
        with open(u, 'wb') as t:
            t.write(upload_file.read())
            upload_file.seek(0, 0)

        if not is_pe(upload_file):
            return jsonify({
                'status': 'error',
                'msg': 'is not a pe file!',
                'filename': id
            })
        elif self.task_executor.status(id) in ('running', 'done', 'reported'):
            return jsonify({
                'status': 'success',
                'msg': 'task finished',
                'filename': id
            })
        else:
            self.task_executor.submit(id, upath)
            return jsonify({
                'status': 'success',
                'msg': 'task appended to the queue',
                'filename': id
            })

    def status(self, id):
        """
        return status of a task

        :param id: task id 
        :return: could be empty|running|done|reported|exception
        """
        return self.task_executor.status(id)

    def left_cnt(self):
        """
        how many task running currently    
        """
        return str(self.task_executor.left_cnt())
    
    def running_list(self):
        """
        running task list
        """
        return jsonify(self.task_executor.running_list())

    def pending_list(self):
        """
        pending task list
        """
        return jsonify(self.task_executor.pending_list())

    def pending_cnt(self):
        """
        pending task cnt
        """
        return jsonify(self.task_executor.pending_cnt())
