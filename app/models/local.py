from mongoengine import *

from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import DateTimeField, DictField, FileField, ListField, StringField

class Local(Document):
    task_id = StringField(primary_key=True)
    asm_file = FileField(required=True)  
    bytes_file = FileField(required=True) 
    bmp_file = FileField(required=True)   
    malware_classification_resnet34 = DictField(required=True)  
    malware_sim_doc2vec = ListField(required=True)              

    meta = {'collection': 'local'}  # 存储在名为local的collection中