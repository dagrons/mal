from flask import current_app

from app.models.feature import *        # 与数据库交互

import concurrent.futures

from .asyncext.FlaskThread import FlaskThread
from .asyncext.SyncQueue import SyncQueue
from .utils.to_neo4j import to_neo4j

from .subtasks import local_analyze, cuckoo_analyze

"""
任务队列
"""
Q = SyncQueue()  # => task_id

"""
全局线程池
"""
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

"""
分析任务
"""


def analyze(task):
    try:
        res = Feature(task_id=task['id'])
        with open(task['upload'], 'rb') as f:
            res.upload.put(f)

        """
        开始分析
        这里之所以用两个线程进行处理是为了可扩展性
        """
        subtasks = {
            'local': FlaskThread(target=local_analyze, args=[task, res]),
            'cuckoo': FlaskThread(target=cuckoo_analyze, args=[task, res])
        }

        for k, v in subtasks.items():
            v.start()

        for k, v in subtasks.items():
            v.join()

        if (task['status'] == 'error'):
            Q.remove(task)
            current_app.logger.info(
                "task ({}) 任务失败, 当前剩余任务({})".format(task['id'], len(Q.q)))
            return

        to_neo4j(current_app.neo, res.to_json(), task['id'])  # 保存结果到Neo4J
        res.save()
        current_app.logger.info("task ({}) 任务结果入库完成".format(task['id']))
        """"
        分析完毕或失败，任务都要出队
        """
    except:
        Q.remove(task)
        current_app.logger.info(
            "task ({}) 任务失败, 当前剩余任务({})".format(task['id'], len(Q.q)))
    else:
        Q.remove(task)
        current_app.logger.info(
            "task ({}) 任务完成, 当前剩余任务({})".format(task['id'], len(Q.q)))
