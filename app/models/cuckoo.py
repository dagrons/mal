from mongoengine import *
import datetime


class Info(EmbeddedDocument):
    package = StringField(required=True)     # exe, elf...
    platform = StringField(required=True)    # linux/win7/...


class Target(EmbeddedDocument):
    # fingerprint
    md5 = StringField(required=True)
    urls = ListField(StringField())  # may contains author information
    name = StringField(required=True)             # filename


class Static(EmbeddedDocument):
    strings = ListField(StringField(), required=True)  # 字符串信息
    pe_imports = ListField(required=True)              # 导入表信息
    pe_exports = ListField()                           # 导出表信息
    pe_resources = ListField()                         # 资源表信息
    pe_sections = ListField(required=True)             # 节段表信息
    pe_timestamp = DateTimeField(
        default=datetime.datetime.utcnow, required=True)  # 出现时间


class Behavior(EmbeddedDocument):  # 都可能为空
    generic = ListField()
    file_opened = ListField(StringField())
    file_created = ListField(StringField())
    file_recreated = ListField(StringField())
    file_exists = ListField(StringField())
    file_read = ListField(StringField())
    file_written = ListField(StringField())
    file_failed = ListField(StringField())
    directory_created = ListField(StringField())
    dll_loaded = ListField(StringField())
    mutex = ListField(StringField())
    regkey_written = ListField(StringField())
    regkey_opened = ListField(StringField())
    regkey_read = ListField(StringField())
    command_line = ListField(StringField())
    guid = ListField(StringField())
    extracted = ListField()
    dropped = ListField()
    processes = ListField()   # contains process information, such as pid and modules
    processtree = ListField()  # contains process tree information


class Cuckoo(Document):
    task_id = StringField(primary_key=True)           # 任务id
    upload_time = DateTimeField(default=datetime.datetime.utcnow)  # 样本上传时间
    upload = FileField(required=True)                 # 样本文件
    info = EmbeddedDocumentField(Info, required=True)  # 文件类型信息
    target = EmbeddedDocumentField(Target, required=True)  # 指纹信息
    static = EmbeddedDocumentField(Static, required=True)  # 包含静态信息
    network = DictField(required=True)         # 包含网络行为信息
    behavior = EmbeddedDocumentField(Behavior)  # 系统行为信息
    signatures = ListField()                     # signature信息
    debug = DictField(required=True)  # 沙箱debug信息
    _buffer = ListField()  # 缓冲区分析信息，buffer为python保留关键字
    procmemory = ListField()    # 内存分布信息

    meta = {'collection': 'cuckoo'}  # 存储在名为cuckoo的collection中
