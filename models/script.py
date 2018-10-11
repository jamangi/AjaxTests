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
    user_id = ''
    material = 0
    location = 'training'
    filename = ''
    filetext = ''
    filetype = 'bash'
    row = 0
    col = 0

    def __init__(self):
    	self.collected = {}

    def collect(self, user_id):
    	if self.collected.get(user_id) is None:
    		self.collected[user_id] = True
    		return True
    	else:
    		return None