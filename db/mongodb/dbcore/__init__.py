from .mongo import getDb, connect2db

# if somebody does "from somepackage import *", this is what they will
# be able to access:
__all__ = [
    'getDb',
    'connect2db'
]
