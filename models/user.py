#!/usr/bin/python3
'''
    Class representing a User
'''
from models.base_model import BaseModel
import models
import os

class User(BaseModel):
    '''
        Definition of the User class
    '''
    ip = ''
    container_name = ''

    name = ''
    location = 'training'
    form = 'dog'
    character = 'titan'
    scripts_held = 10
    script_limit = 20
    material = 0

    total_collected = 0
    total_dropped = 0
    row = -1
    col = -1 # updated on drop
    
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
    	if self.scripts_held < self.script_limit:
    		self.scripts_held = self.scripts_held + 1
    		return self.scripts_held
    	else:
    		return None;

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