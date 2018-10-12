import models
from models.base_model import BaseModel
from models.user import User
from models.script import Script

def create(classname=None, **kwargs):
	'''
		Create a new instance of class BaseModel and saves it
		to the JSON file.
	'''
	if classname is None:
		print("** class name missing **")
		return None
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
def get(classname=None, id):
	'''
		Get object by id
	'''
	if classname is None:
		print("** class name missing **")
		return None
	instance = models.storage.get(classname, id)
	return instance

def get_user_by_ip(ip):
	'''
		Searches for user by IP
	'''
	result = User.search_by_ip(ip)
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