import tempfile
import time
from flask import current_app
import concurrent.futures
import requests

from app.models.feature import *
from app.utils.transform import get_asm_from_bytes, get_bytes_from_file
from app.utils.malware_classification.scripts.transform import pe2bmp
from app.utils.malware_classification.predict import predict as predict_cls
from app.utils.malware_sim.predict import predict as predict_sim


class TaskExecutor():
    """
    TaskExecutor is the task manager for malware analysis
    """

    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=current_app.config['MAX_WORKERS'])
        self.futures = {}

    def submit(self, id, file):
        """
        submit a task to be executed

        :param id: task id
        :param file: uploaded file
        """
        def execute(app, id, f):
            """
            async task

            :param app: app object of flask, for async task, we usually need app_context
            :param id: is the task id
            :param file: is the file to be processed
            """
            with app.app_context():
                res = Feature(task_id=id)
                with open(f, 'rb') as fp:                    
                    res.upload.put(fp)

                """
                model analysis
                """
                current_app.logger.info("task ({}) 开始进行本地分析".format(id))
                upath = f  # upath: upload path
                af, afpath = tempfile.mkstemp(
                    suffix='.asm')  # contians only opcode
                # contains only .text section
                bf, bfpath = tempfile.mkstemp(suffix='.bytes')
                # contains only .text, .data, .rdata sections
                pf, pfpath = tempfile.mkstemp(suffix='.bmp')

                get_bytes_from_file(upath, bfpath)
                get_asm_from_bytes(bfpath, afpath)

                try:
                    pe2bmp(upath, pfpath)
                    res.bmp_file.put(open(pf, 'rb'))
                except:
                    """
                    the malware may be packed 
                    """
                    pass

                res.local = Local()

                res.local.asm_file.put(open(af, 'rb'))
                res.local.bytes_file.put(open(bf, 'rb'))
                res.local.bmp_file.put(open(pf, 'rb'))

                res.local.malware_classification_resnet34 = predict_cls(pfpath)
                res.local.malware_sim_doc2vec = predict_sim(bfpath)

                # 将概率列表转化为概率字典
                t = {}
                prob_families = ['Ramnit', 'Lollipop', 'Kelihos_ver3', 'Vundo',
                                 'Simda', 'Tracur', 'Kelihos_ver1', 'Obfuscator', 'Gatak']
                for k, v in zip(prob_families, res.local.malware_classification_resnet34):
                    t[k] = v
                res.local.malware_classification_resnet34 = t
                current_app.logger.info("task ({}) 本地分析结束".format(id))

                """
                cuckoo analysis
                """
                current_app.logger.info("task ({}) 开始进行沙箱分析".format(id))
                try:
                    file = {"file": (res.task_id, res.upload)}
                    headers = {
                        "Authorization": current_app.config['CUCKOO_TOKEN']}
                    r = requests.post(
                        current_app.config['CUCKOO_URL'] +
                        '/tasks/create/file',
                        files=file,
                        headers=headers)
                    cuckoo_task_id = str(r.json()['task_id'])
                except:
                    current_app.logger.error("无法连接到沙箱，请检查与沙箱的网络连接")
                    raise

                current_app.logger.info(
                    'task ({}) 成功上传文件到沙箱, 沙箱任务id=({})'.format(id, cuckoo_task_id))

                done = False
                while not done:
                    time.sleep(3)
                    r = requests.get(
                        current_app.config['CUCKOO_URL'] +
                        '/tasks/view/' + str(cuckoo_task_id),
                        headers=headers)
                    if r.json()['task']['status'] == "reported":
                        done = True
                try:
                    cuckoo_report = requests.get(
                        current_app.config['CUCKOO_URL'] +
                        '/tasks/report/' + str(cuckoo_task_id),
                        headers=headers).json()
                except:
                    current_app.logger.info(
                        'task ({}) 获取沙箱报告失败， 沙箱任务id=({})'.format(id, cuckoo_task_id))
                    raise
                current_app.logger.info(
                    'task ({}) 成功获取沙箱报告，沙箱任务id=({})'.format(id, cuckoo_task_id))

                # sanity_correct
                def sanity_correct(d, k):
                    if type(d[k]) == str:
                        try:
                            d[k] = d[k].encode(
                                'utf-16', 'surrogatepass').decode('utf-16')
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
                current_app.logger.info(
                    'task ({} 沙箱报告编码处理完毕，准备预处理)'.format(id))

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
                            'task ({}) 沙箱报告中缺乏动态特征字段'.format(id))
                        pass

                    for ops in ['file_opened', 'file_created', 'file_recreated', 'file_read', 'file_written', 'file_failed', 'directory_created', 'dll_loaded', 'mutex', 'regkey_opened', 'regkey_read', 'regkey_written', 'command_line', 'guid', 'extracted', 'dropped']:
                        try:
                            setattr(res.behavior, ops,
                                    report['behavior']['summary'][ops])
                        except KeyError:
                            pass            # 忽略缺失字段
                    try:
                        res.signatures = report['signatures']
                    except KeyError:    # signature为可选字段
                        pass

                    res.network = report['network']
                    res.debug = report['debug']

                preprocessing(res, cuckoo_report)
                current_app.logger.info('task ({}) 沙箱报告预处理完毕)'.format(id))
                current_app.logger.info("task ({}) 沙箱分析结束".format(id))

                res.validate()
                res.save()

        self.futures[id] = self.executor.submit(
            execute, current_app._get_current_object(), id, file)

    def status(self, id):
        """
        Check the status of a task
        if it has already in database, return "done"
        if not in queue or database, return "empty"
        NOTE: when exception happens, the task are finished too!

        :param id: task id generated by cuckoo
        :return: "running", "done", ...     
        """
        if len(Feature.objects(task_id=id)) >= 1:
            return "reported"
        elif id in self.futures:
            if self.futures[id].running():
                return "running"
            elif self.futures[id].exception():
                return "exception"
            else:
                return "done"
        else:
            return "empty"

    def left_cnt(self):
        """
        count of task not reported
        """
        return len([id for id, f in self.futures if f.running()])