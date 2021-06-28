import hashlib
from app.models.cuckoo import *


def compute_md5(f):
    f_hash = hashlib.md5()
    line = f.readline()
    while (line):
        f_hash.update(line)
        line = f.readline()
    filename = f_hash.hexdigest()
    f.seek(0, 0)

    return filename


def preprocessing(report):
    res = Cuckoo()

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

    return res

