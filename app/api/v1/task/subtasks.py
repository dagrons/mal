from flask import Blueprint, current_app, request, render_template, jsonify, session, redirect

from app.models.feature import *        # 与数据库交互

import ujson as json  # json.load(fp), json.loads(str), json.dumps(dict)
import requests       # 用来进行网络请求
import tempfile       # 用于创建临时文件
import time           # 用于sleep之类的操作
import datetime       # 处理日期时间

from .utils.local import analyze as model_analyze  # 模型分析
from .utils.cuckoo import query_task, get_report   # 沙箱通信
from .utils.transform import get_asm_from_bytes, get_bytes_from_file  # 格式转换
from .utils.malware_classification.scripts.transform import pe2bmp
from .utils.utils import compute_md5  # hash计算

"""
本地分析
"""


def local_analyze(task, res):
    """
    生成asm, bytes, png, 并得到对应的模型分析结果
    """

    current_app.logger.info("task ({}) 开始进行本地分析".format(task['id']))
    upath = task['upload']

    af, afpath = tempfile.mkstemp(suffix='.asm')  # 只包含opcode
    bf, bfpath = tempfile.mkstemp(suffix='.bytes')  # 只包含text区段
    pf, pfpath = tempfile.mkstemp(suffix='.bmp')   # 包含text, data, rdata区段

    get_bytes_from_file(upath, bfpath)
    get_asm_from_bytes(bfpath, afpath)


    try:
        pe2bmp(upath, pfpath)
    except:
        task['status'] = 'error'
        task['msg'] = '.text, .data, or .rdata sections are not found!'
        return

    res.local = Local()
    res.local.asm_file.put(open(af, 'rb'))
    res.local.bytes_file.put(open(bf, 'rb'))
    res.local.bmp_file.put(open(pf, 'rb'))

    res.local.malware_classification_resnet34, res.local.malware_sim_doc2vec = model_analyze(
        bfpath, pfpath)

    # 将概率列表转化为概率字典
    t = {}
    prob_families = ['Ramnit', 'Lollipop', 'Kelihos_ver3', 'Vundo',
                     'Simda', 'Tracur', 'Kelihos_ver1', 'Obfuscator', 'Gatak']
    for k, v in zip(prob_families, res.local.malware_classification_resnet34):
        t[k] = v
    res.local.malware_classification_resnet34 = t

    current_app.logger.info("task ({}) 本地分析结束".format(task['id']))


"""
沙箱分析
"""


def cuckoo_analyze(task, res):
    current_app.logger.info("task ({}) 开始进行沙箱分析".format(task['id']))

    # 上传文件到沙箱
    try:
        url = current_app.config['CUCKOO_URL'] + '/tasks/create/file'
        files = {"file": (res.task_id, res.upload)}
        headers = {"Authorization": "Bearer PYK9j3-G4zyScn4EDW3eKg"}
        r = requests.post(url, files=files, headers=headers)
        cuckoo_task_id = str(r.json()['task_id'])
    except:
        current_app.logger.error("无法连接到沙箱，请检查与沙箱的网络连接")
        raise

    current_app.logger.info(
        'task ({}) 成功上传文件到沙箱, 沙箱任务id=({})'.format(task['id'], cuckoo_task_id))

    # 轮询直到获取到沙箱报告文件
    done = False
    url = current_app.config['CUCKOO_URL'] + '/tasks/view/'
    while (not done):
        time.sleep(3)
        re = query_task(cuckoo_task_id, url)
        if re == "reported":
            done = True
    url = current_app.config['CUCKOO_URL'] + '/tasks/report/'
    try:
        cuckoo_report = get_report(cuckoo_task_id, url)
    except:
        current_app.logger.info(
            'task ({}) 获取沙箱报告失败， 沙箱任务id=({})'.format(task['id'], cuckoo_task_id))
        raise
    current_app.logger.info(
        'task ({}) 成功获取沙箱报告，沙箱任务id=({})'.format(task['id'], cuckoo_task_id))

    # sanity_correct
    def sanity_correct(d, k):
        if type(d[k]) == str:
            try:
                d[k] = d[k].encode('utf-16', 'surrogatepass').decode('utf-16')
            except UnicodeDecodeError:
                d[k] = ascii(d[k])
                pass
        elif type(d[k]) == list:
            for i in range(len(d[k])):
                sanity_correct(d[k], i)
        elif type(d[k]) == dict:
            for i in d[k].keys():
                sanity_correct(d[k], i)
        else:
            return

    sanity_correct({'report': cuckoo_report}, 'report')
    current_app.logger.info('task ({} 沙箱报告编码处理完毕，准备预处理)'.format(task['id']))

    # 预处理响应沙箱报告文件到res中
    def preprocessing(res, report):

        res.info = Info()
        res.info.package = report['info']['package']
        res.info.platform = report['info']['platform']

        res.target = Target()
        res.target.md5 = report['target']['file']['md5']
        res.target.urls = report['target']['file']['urls']
        res.target.name = report['target']['file']['name']

        res.static = Static()
        res.static.strings = report['strings']
        res.static.pe_imports = report['static']['pe_imports']
        res.static.pe_exports = report['static']['pe_exports']
        res.static.pe_resources = report['static']['pe_resources']
        res.static.pe_sections = report['static']['pe_sections']
        if 'pe_timestamp' in report['static']:
            res.static.pe_timestamp = datetime.datetime.strptime(
                report['static']['pe_timestamp'], '%Y-%m-%d %H:%M:%S')
        else:
            res.static.pe_timestamp = datetime.datetime.now()

        try:
            res.procmemory = report['procmemory']
        except KeyError:    # procmemory为可选字段
            pass

        try:
            res._buffer = report['buffer']
        except KeyError:    # buffer为可选字段
            pass

        try:
            res.behavior = Behavior()
            res.behavior.generic = report['behavior']['generic']
            res.behavior.processes = report['behavior']['processes']
            res.behavior.processtree = report['behavior']['processtree']
        except KeyError:    # behavior为可选字段
            current_app.logger.warning(
                'task ({}) 沙箱报告中缺乏动态特征字段'.format(task['id']))
            pass

        for ops in ['file_opened', 'file_created', 'file_recreated', 'file_read', 'file_written', 'file_failed', 'directory_created', 'dll_loaded', 'mutex', 'regkey_opened', 'regkey_read', 'regkey_written', 'command_line', 'guid', 'extracted', 'dropped']:
            try:
                setattr(res.behavior, ops, report['behavior']['summary'][ops])
            except KeyError:
                pass            # 忽略缺失字段
        try:
            res.signatures = report['signatures']
        except KeyError:    # signature为可选字段
            pass

        res.network = report['network']
        res.debug = report['debug']

    preprocessing(res, cuckoo_report)
    current_app.logger.info('task ({}) 沙箱报告预处理完毕)'.format(task['id']))
    current_app.logger.info("task ({}) 沙箱分析结束".format(task['id']))
