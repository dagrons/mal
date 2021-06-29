# cuckoo交互
"""
与cuckoo交互
向cuckoo提交任务，查询任务状态，从cuckoo获取report，解析report
"""

import os
import time
import requests
import json
import os

def query_task(task_id, cuckoo_url):
    """
    询问任务的状态是否已完成，返回"pending running completed reported"等
    如果task_id不存在，会返回{ message: Task not found }

    TODO: 异常处理

    :param task_id:
    :param cuckoo_url: http://xxx/tasks/view/1
    """
    headers = {"Authorization": "Bearer PYK9j3-G4zyScn4EDW3eKg"}
    r = requests.get(cuckoo_url + task_id, headers=headers)
    res = r.json()["task"]["status"]
    return res

def get_report(task_id, cuckoo_url):
    """
    根据task_id获取对应的report(json格式），前提是query_task返回"Done"

    TODO: 异常处理

    :param task_id:
    :param cuckoo_url: http://xxx/tasks/report/1
    """
    headers = {"Authorization": "Bearer PYK9j3-G4zyScn4EDW3eKg"}
    res = requests.get(cuckoo_url + task_id, headers=headers)
    return res.json()
