from app.models.local import Local
from .local import LocalExecutor
from .cuckoo import CuckooExecutor

local_executor = LocalExecutor()
cuckoo_executor = CuckooExecutor()
