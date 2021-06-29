import json
import hashlib
import requests       # 用来进行网络请求
import tempfile
import logging

from flask import Blueprint, current_app, request, render_template, jsonify, session, redirect

from app.models.feature import *
from .tasks import Q, analyze, executor
from .asyncext.FlaskTask import FlaskTask

task_bp = Blueprint('task', __name__)

"""
文件上传
"""


@task_bp.route('/create', methods=['POST'])
def create():
    """
    用md5作为任务id
    """

    upload = request.files['file']
    md5 = hashlib.md5(upload.read()).hexdigest()
    upload.seek(0, 0)

    if not isPe(upload):
        return jsonify({
            'status': 'error',
            'msg': 'is not a pe file!',
            'filename': md5
        })

    """
    过滤重复任务
    """
    with Q.lock:
        # 数据库中是否已经存在该任务
        if len(Feature.objects(task_id=md5)) >= 1 or md5 in [t['id'] for t in Q.q]:
            return jsonify({
                'status': 'success',
                'msg': 'task finished',
                'filename': md5
            })

    """
    tips: 保存上传文件，传递给其他线程，request生命周期只在当前线程，包括上传文件FileStorage对象也是
    """
    f, fpath = tempfile.mkstemp()
    with open(f, 'wb') as t:
        t.write(upload.read())
        upload.seek(0, 0)

    """
    创建任务
    """
    task = {
        'id': md5,
        'upload': fpath,
        'status': 'running',
        'msg': ''
    }
    task['future'] = executor.submit(FlaskTask(analyze, task))
    Q.put(task)

    current_app.logger.info(
        "task ({}) 开始执行，当前剩余任务({})".format(task['id'], len(Q.q)))

    return jsonify(
        {
            'status': 'success',
            'msg': 'task appened to the queue',
            'filename': task['id']
        })


"""
任务列表
"""


@task_bp.route('/query/list')
def all():
    with Q.lock:
        return json.dumps([t['id'] for t in Q.q])


@task_bp.route('/query/cnt')
def cnt():
    return str(len(Q.q))


def isPe(fp):

    flag1 = fp.read(2)  # 读取文件前两个字节
    fp.seek(0x3c)  # 获取PE头偏移
    offset = ord(fp.read(1))
    fp.seek(offset)
    flag2 = fp.read(4)  # 获取PE头签名
    fp.seek(0, 0)
    if flag1 == b'MZ' and flag2 == b'PE\x00\x00':  # 判断是否为PE文件的典型特征签名
        return True
    return False
