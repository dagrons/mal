from flask_mongoengine import MongoEngine
from .neo4j import Neo
from .cuckoo import CuckooExecutor
from .local import LocalExecutor

mongo = MongoEngine()
neo = Neo()
cuckoo_executor = CuckooExecutor()
local_executor = LocalExecutor()
