"""
特征展示页面接口
"""

from flask import Blueprint, request, current_app, send_file, render_template, jsonify, session, redirect, abort

import ujson as json
import time
import numpy as np

from app.models.feature import *
from .task.tasks import Q

feature_bp = Blueprint('feature', __name__)


@feature_bp.route('/report/get/<filename>')
def get_report(filename):
    """
    获取报告
    """
    # 任务仍在队列中

    for t in Q.q:
        if t['id'] == filename:
            if (t['status'] == 'error'):
                return jsonify({
                    'status': 'error',
                    'msg': t['msg'],
                    'isvalid': False
                })
            else:
                return jsonify({
                    'status': 'running',
                    'msg': 'the task is still running',
                    'isvalid': True,
                })

    # 任务不在队列中，且数据库中不存在
    if len(Feature.objects(task_id=filename)) < 1:
        return jsonify({
            'status': 'error',
            'msg': 'the file do not exists',
            'isvalid': False,
        })

    # 任务已入库
    report = Feature.objects(task_id=filename).first()

    ts = Feature.objects.only('task_id').only('local.malware_sim_doc2vec')
    vec1 = np.array(report.local.malware_sim_doc2vec)
    sims = []
    for t in ts:
        vec2 = np.array(t.local.malware_sim_doc2vec)
        sims.append((t.task_id, np.dot(vec1, vec2) /
                    (np.linalg.norm(vec1)*np.linalg.norm(vec2))))
    sorted(sims, key=lambda x: -x[1])

    return jsonify({
        'status': 'reported',
        'msg': 'reported',
        'isvalid': True,
        'report': report,
        'five_most_like': sims[1:6]
    })


@feature_bp.route('/bmp/get/<filename>')
def get_png(filename):
    if len(Feature.objects(task_id=filename)) < 1:
        abort(404)
    return send_file(Feature.objects(task_id=filename).first().local.bmp_file, attachment_filename=filename+'.bmp')

@feature_bp.route('/dashboard')
def dashboard():
    res = {}

    # for counting 
    res['samples_count'] = Feature.objects.count()  # 当前数据库已有的样本数
    res['current_count'] = len(Q.q)                 # 正在处理样本数
    res['recent_count'] = Feature.objects(upload_time__gte=datetime.datetime.utcnow()-datetime.timedelta(days=7)).count()  # 取过去7天内上传的文件数


    # for family distribution
    type_res = {}
    for type in ['Ramnit', 'Lollipop', 'Kelihos_ver3', 'Vundo', 'Simda', 'Tracur', 'Kelihos_ver1', 'Obfuscator', 'Gatak']:
        type_res[type] = 0
    overall_sum = 0

    all_locals = Feature.objects.only('local.malware_classification_resnet34')
    for t in all_locals:
        max_type = None
        for type in ['Ramnit', 'Lollipop', 'Kelihos_ver3', 'Vundo', 'Simda', 'Tracur', 'Kelihos_ver1', 'Obfuscator', 'Gatak']:
            if max_type == None or t.local.malware_classification_resnet34[type] >= t.local.malware_classification_resnet34[max_type]:
                max_type = type
        type_res[max_type] += 1
    res['type_res'] = type_res

    # for trend area
    trend_area = []
    year_ranges = []
    end_of_range = datetime.datetime.today().date()  # 到xx年
    for t in range(20):
        year_ranges.append(end_of_range - datetime.timedelta(days=365*t))        
    year_ranges.reverse()
    
    ts = Feature.objects().only('static.pe_timestamp')
    for y in year_ranges:
        cnt = 0
        for t in ts:
            if t.static.pe_timestamp.date() <= y:
               cnt += 1
        trend_area.append(cnt)
    res['trend_area'] = trend_area

    return jsonify(res)