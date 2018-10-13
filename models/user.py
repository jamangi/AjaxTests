#!/usr/bin/python3
'''
    Class representing a User
'''
from datetime import datetime
import os

import models
from models.base_model import BaseModel

class User(BaseModel):
    '''
        Definition of the User class
    '''
    def __init__(self, *args, **kwargs):
        self.ip = ''
        self.container_version = 0

        self.name = ''
        self.location = 'training'
        self.base_form = 'dog'
        self.form = 'dog'
        self.character = 'titan'
        self.scripts_held = 8
        self.script_limit = 10
        self.material = 0

        self.total_collected = 0
        self.total_dropped = 0
        self.row = 0
        self.col = 0 # updated on drop
        super().__init__(*args, **kwargs)
    
    @staticmethod
    def search_by_ip(ip):
    	'''
    		Search by ip address
    	'''
    	all_users = models.storage.all('User')
    	for user in all_users.values():
    		if user.ip == ip:
    			return user
    	return None

    def touch(self):
        '''
            Update the updated_at attribute without saving to disk.
        '''
        self.updated_at = datetime.now()

    def add_material(self, amount):
    	'''
    		Update material
    	'''
    	self.material = self.material + amount
    	if self.material < 0:
    		self.material = 0
    	return self.material

    def add_script(self):
    	'''
    		Try to add script
    	'''
    	if self.has_space():
    		self.scripts_held = self.scripts_held + 1
    		return self.scripts_held
    	else:
    		return None;

    def has_space(self):
        '''
            Checks if scripts held at limit
        '''
        if self.scripts_held < self.script_limit:
            return True
        else:
            return False

    def get_scripts(self):
    	'''
    		Get all scripts authored by user
    	'''
    	scripts = []
    	all_scripts = models.storage.all('Script')
    	for v in all_scripts.values():
    		if v.user_id == self.id:
    			scripts.append(v)
    	return scripts

    def pay_material(self, amount):
        '''
            Pay material
        '''
        if amount > self.material:
            paid = self.material
        else:
            paid = amount

        self.add_material(amount * -1)
        return paid

    def use_material(self, amount):
    	'''
    		Try to use material
    	'''
    	if self.material < amount:
    		return None
    	else:
    		self.material = self.material - amount

    def use_script(self):
    	'''
    		Try to use script
    	'''
    	if self.scripts_held > 0:
    		self.scripts_held = self.scripts_held - 1
    		return self.scripts_held
    	else:
    		return None