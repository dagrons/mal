import logging
import logging.config
from typing import Dict

class TaskLogFilter(logging.Filter):
    """
    This filter only show log entries for specified thread name
    """

    def __init__(self, task_id, *args, **kwargs):
        logging.Filter.__init__(self, *args, **kwargs)
        self.task_id = task_id

    def filter(self, record):
        if type(record.args) is dict:
            return record.args.get('task_id') == self.task_id
        else:
            return False

def start_task_logging(task_id):
    """
    Add a log handler to separate file for current thread
    """
    log_file = '/tmp/perTaskLogging-{}.log'.format(task_id)
    log_handler = logging.FileHandler(log_file)

    log_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)-15s"        
        "| %(levelname)-5s"
        "| %(message)s")
    log_handler.setFormatter(formatter)

    log_filter = TaskLogFilter(task_id)
    log_handler.addFilter(log_filter)

    logger = logging.getLogger()
    logger.addHandler(log_handler)

    return log_handler

def stop_task_logging(log_handler):
    # Remove thread log handler from root logger
    logging.getLogger().removeHandler(log_handler)

    # Close the thread log handler so that the lock on log file can be released
    log_handler.close()
