#!/usr/bin/python3
'''
    Package initializer
'''

from models.base_model import BaseModel
from models.user import User
from models.script import Script
from models.engine.file_storage import FileStorage

classes = {"User": User, "BaseModel": BaseModel, "Script": Script}

storage = FileStorage()
storage.reload()