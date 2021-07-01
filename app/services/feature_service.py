import numpy as np
from app.models.feature import *


class FeatureService():
    """
    FeatureService serves all infos about malware features and database statistics
    """
    def __init__(self, task_executor):
        self.task_executor = task_executor

    def dashboard(self):
        """
        return the statistic infos for dashboard page
        """
        res = {}

        # for counting
        res['samples_count'] = Feature.objects.count()  # 当前数据库已有的样本数
        res['current_count'] = self.task_executor.left_cnt()                # 正在处理样本数
        res['recent_count'] = Feature.objects(upload_time__gte=datetime.datetime.utcnow(
        )-datetime.timedelta(days=7)).count()  # 取过去7天内上传的文件数

        # for family distribution
        type_res = {}
        for type in ['Ramnit', 'Lollipop', 'Kelihos_ver3', 'Vundo', 'Simda', 'Tracur', 'Kelihos_ver1', 'Obfuscator', 'Gatak']:
            type_res[type] = 0

        all_locals = Feature.objects.only(
            'local.malware_classification_resnet34')
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

        return res

    def get_report(self, id):
        """
        get the result of a reported task
        if not reported, return None
        NOTE: the most 5 similar malware samples was computed 

        :param id: task id
        :return: result if task reported else None
        """
        if len(Feature.objects(task_id=id)) >= 1:
            return Feature.objects(task_id=id).first()
        else:
            return None

    def top_5_similar(self, vec):
        """
        return the top 5 similar samples id

        :param vec: the doc2vec of the malware
        :return: the most five similar malwares id
        """
        ts = Feature.objects.only('task_id').only('local.malware_sim_doc2vec')
        sims = []
        for t in ts:
            vec2 = np.array(t.local.malware_sim_doc2vec)
            sims.append((t.task_id, np.dot(vec, vec2) /
                        (np.linalg.norm(vec)*np.linalg.norm(vec2))))
        sorted(sims, key=lambda x: -x[1])
        return sims[1:6]

    def get_png(self, filename):
        """
        get the png file of task
        if task id does not exist, return None

        :param filename: task id
        :return: None or file
        """
        if len(Feature.objects(task_id=filename)) < 1:
            return None
        else:
            return Feature.objects(task_id=filename).first().local.bmp_file

    def get_cfg(self, filename):
        """
        get cfg(svg) file of task

        :param filename: task id
        :return: None or file
        """
        if len(Feature.objects(task_id=filename)) < 1:
            return None
        else:
            return Feature.objects(task_id=filename).first().local.cfg_file