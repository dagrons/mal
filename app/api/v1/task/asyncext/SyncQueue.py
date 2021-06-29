import threading

"""
实现一个同步的任务队列
"""
class SyncQueue():
    def __init__(self):
        self.q = []
        self.lock = threading.Lock()

    def put(self, item):
        with self.lock:
            self.q.append(item)
    
    def remove(self, item):
        with self.lock:
            self.q.remove(item)
