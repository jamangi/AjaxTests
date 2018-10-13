#!/usr/bin/python3
'''
    Class representing a Script
'''
from models.base_model import BaseModel
import models
import os

class Script(BaseModel):
    '''
        Definition of the Script class
    '''
    def __init__(self, *args, **kwargs):
        self.user_id = ''
        self.material = 0
        self.location = 'training'
        self.filename = ''
        self.filetext = ''
        self.filetype = 'bash'
        self.row = 0
        self.col = 0
        self.collected = {}
        super().__init__(*args, **kwargs)

    def collected(self, user_id):
        if self.collected.get(user_id) is None:
            return False
        else:
            return True

    def collect(self, user_id):
		self.collected[user_id] = True
        self.save()