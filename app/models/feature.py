"""
特征报告的数据库模式：半结构化的数据
"""

"""
it's always a good practice to define a schema even for semi-structued data
除非是要进行数学运算，否则不要用IntField
多用required=true，这样取出来的时候就不会有那么多bug
"""
from mongoengine import *
import datetime

"""
文件类型信息
"""
class Info(EmbeddedDocument):
    package = StringField(required=True)     # exe, elf...
    platform = StringField(required=True)    # linux/win7/...

"""
指纹信息
"""
class Target(EmbeddedDocument):
    # fingerprint
    md5 = StringField(required=True)
    urls = ListField(StringField())  # may contains author information
    name = StringField(required=True)             # filename


"""
静态特征信息
"""
class Static(EmbeddedDocument):
    strings = ListField(StringField(), required=True)  # 字符串信息
    pe_imports = ListField(required=True)              # 导入表信息
    pe_exports = ListField()                           # 导出表信息
    pe_resources = ListField()                         # 资源表信息
    pe_sections = ListField(required=True)             # 节段表信息
    pe_timestamp = DateTimeField(default=datetime.datetime.utcnow, required=True)  # 出现时间    
    
"""
系统行为信息，都是非必填字段
"""
class Behavior(EmbeddedDocument):  # 都可能为空
    # 详细信息
    generic = ListField()
    # 文件操作
    file_opened = ListField(StringField())
    file_created = ListField(StringField())
    file_recreated = ListField(StringField())
    file_exists = ListField(StringField())
    file_read = ListField(StringField())
    file_written = ListField(StringField())
    file_failed = ListField(StringField())
    directory_created = ListField(StringField())
    # 动态链接库
    dll_loaded = ListField(StringField())
    # 互斥量                     
    mutex = ListField(StringField())    
    # 注册表
    regkey_written = ListField(StringField())
    regkey_opened = ListField(StringField())
    regkey_read = ListField(StringField())
    # 命令行
    command_line = ListField(StringField())
    # guid
    guid = ListField(StringField())
    # extracted
    extracted = ListField()
    # dropped
    dropped = ListField()
    # 进程信息
    processes = ListField()   # contains process information, such as pid and modules
    processtree = ListField()  # contains process tree information

"""
模型分析信息
"""
class Local(EmbeddedDocument):
    """
    模型分析相关文件
    """
    asm_file = FileField(required=True)  # 只包含text区段
    bytes_file = FileField(required=True)  # 只包含text区段
    bmp_file = FileField(required=True)    # 包含text, data, rdata区段
    """
    模型分析结果
    """
    malware_classification_resnet34 = DictField(required=True)  # 使用malware_classifcation resnet34模型进行判定的结果
    malware_sim_doc2vec = ListField(required=True)              # 使用Doc2Vec得到的向量
    
"""
Schema for report
"""
class Feature(Document):
    task_id = StringField(primary_key=True)           # 任务id
    upload_time = DateTimeField(default=datetime.datetime.utcnow)  # 样本上传时间
    upload = FileField(required=True)                 # 样本文件
    info = EmbeddedDocumentField(Info, required=True)  # 文件类型信息
    target = EmbeddedDocumentField(Target, required=True)  # 指纹信息
    static = EmbeddedDocumentField(Static, required=True)  # 包含静态信息
    network = DictField(required=True)         # 包含网络行为信息
    behavior = EmbeddedDocumentField(Behavior)  # 系统行为信息
    signatures = ListField()                     # signature信息
    local = EmbeddedDocumentField(Local, required=True)  # 模型分析信息
    debug = DictField(required=True)  # 沙箱debug信息
    _buffer = ListField()  # 缓冲区分析信息，buffer为python保留关键字
    procmemory = ListField()    # 内存分布信息
    
    meta = {'collection': 'features'}  # 存储在名为feature的collection中