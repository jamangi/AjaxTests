import models
from models.base_model import BaseModel
from models.user import User
from models.script import Script
from models.map import Map

def create(classname, **kwargs):
	'''
		Create a new instance of class BaseModel and saves it
		to the JSON file.
	'''
	try:
		new_instance = eval(classname)()
		for key, value in kwargs.items():
		    setattr(new_instance, key, value)
		new_instance.save()
		return new_instance

	except Exception as e:
		print("** create instance error **")
		print(e)
		return None
def get(classname, id):
	'''
		Get object by id
	'''
	instance = models.storage.get(classname, id)
	return instance

def get_user_by_ip(ip):
	'''
		Searches for user by IP
	'''
	result = User.search_by_ip(ip)
	return result

def get_scripts(location=None):
	'''
		Searches for scripts in given location
	'''
	result = Script.get_scripts(location)
	return result

def update(ip, **kwargs):
	'''
		Update instance to have desired attributes
	'''
	instance = get_user_by_ip(ip)
	if instance is None:
		print("** instance required **")
		return None
	try:
		for key, value in kwargs.items():
			setattr(instance, key, value)
		instance.save()
		return instance

	except Exception as e:
		print("** update instance error **")
		return None

def save():
	'''
		Saves changes to db
	'''
	models.storage.save()
