#!/usr/bin/python3
'''
    Implementing the console for the HBnB project.
'''
import cmd
import json
import shlex
import models
from models.base_model import BaseModel
from models.user import User
from models.script import Script


class DockerHeartsCommand(cmd.Cmd):
    '''
        Contains the entry point of the command interpreter.
    '''

    prompt = ("(DHV3) ")

    def do_echo(self, args):
        """
        Echo method
        """
        print(args)
        print(type(args))

    def do_quit(self, args):
        '''
            Quit command to exit the program.
        '''
        return True

    def do_EOF(self, args):
        '''
            Exits after receiving the EOF signal.
        '''
        return True

    def do_create(self, args):
        '''
            Create a new instance of class BaseModel and saves it
            to the JSON file.
        '''
        if len(args) == 0:
            print("** class name missing **")
            return
        try:
            args = shlex.split(args)
            kwargs = self.parse_input(args)
            new_instance = eval(args[0])()
            for key, value in kwargs.items():
                setattr(new_instance, key, value)
            new_instance.save()
            print(new_instance.id)

        except Exception as e:
            print("** class doesn't exist **")

    def do_show(self, args):
        '''
            Print the string representation of an instance baed on
            the class name and id given as args.
        '''
        args = shlex.split(args)
        if len(args) == 0:
            print("** class name missing **")
            return
        if len(args) == 1:
            print("** instance id missing **")
            return

        obj_dict = models.storage.all()
        try:
            eval(args[0])
        except NameError:
            print("** class doesn't exist **")
            return
        key = args[0] + "." + args[1]
        key = args[0] + "." + args[1]
        try:
            value = obj_dict[key]
            print(value)
        except KeyError:
            print("** no instance found **")

    def do_destroy(self, args):
        '''
            Deletes an instance based on the class name and id.
        '''
        args = shlex.split(args)
        if len(args) == 0:
            print("** class name missing **")
            return
        elif len(args) == 1:
            print("** instance id missing **")
            return
        class_name = args[0]
        class_id = args[1]

        obj_dict = models.storage.all()
        try:
            eval(class_name)
        except NameError:
            print("** class doesn't exist **")
            return
        key = class_name + "." + class_id
        try:
            del obj_dict[key]
        except KeyError:
            print("** no instance found **")
        models.storage.save()

    def do_all(self, args):
        '''
            Prints all string representation of all instances
            based or not on the class name.
        '''
        obj_list = []
        objects = models.storage.all()
        try:
            if len(args) != 0:
                eval(args)
        except NameError:
            print("** class doesn't exist **")
            return
        for key, val in objects.items():
            if len(args) != 0:
                if type(val) is eval(args):
                    obj_list.append(val)
            else:
                obj_list.append(val)

        print(obj_list)


    def do_update(self, args):
        '''
            Update an instance based on the class name and id
            sent as args.
        '''
        args = shlex.split(args)
        if len(args) == 0:
            print("** class name missing **")
            return
        elif len(args) == 1:
            print("** instance id missing **")
            return
        elif len(args) == 2:
            print("** attribute name missing **")
            return
        elif len(args) == 3:
            print("** value missing **")
            return
        try:
            eval(args[0])
        except NameError:
            print("** class doesn't exist **")
            return
        key = args[0] + "." + args[1]
        obj_dict = models.storage.all()
        try:
            obj_value = obj_dict[key]
        except KeyError:
            print("** no instance found **")
            return
        try:
            attr_type = type(getattr(obj_value, args[2]))
            args[3] = attr_type(args[3])
        except AttributeError:
            pass
        setattr(obj_value, args[2], args[3])
        obj_value.save()

    def emptyline(self):
        '''
            Prevents printing anything when an empty line is passed.
        '''
        pass

    def do_count(self, args):
        '''
            Counts/retrieves the number of instances.
        '''
        obj_list = []
        objects = models.storage.all()
        try:
            if len(args) != 0:
                eval(args)
        except NameError:
            print("** class doesn't exist **")
            return
        for key, val in objects.items():
            if len(args) != 0:
                if type(val) is eval(args):
                    obj_list.append(val)
            else:
                obj_list.append(val)
        print(len(obj_list))


    def default(self, args):
        '''
            Catches all the function names that are not expicitly defined.
        '''
        functions = {"all": self.do_all, "update": self.do_update,
                     "show": self.do_show, "count": self.do_count,
                     "destroy": self.do_destroy, "update": self.do_update}
        args = (args.replace("(", ".").replace(")", ".")
                .replace('"', "").replace(",", "").split("."))

        try:
            cmd_arg = args[0] + " " + args[2]
            func = functions[args[1]]
            func(cmd_arg)
        except Exception:
            print("*** Unknown syntax:", args[0])


    def parse_input(self, args):
        '''
            Parses parameters and returns a dictionary
        '''
        pairs = [arg.split('=') for arg in args[1:]]
        for pair in pairs:
            if '_' in pair[1]:
                pair[1] = pair[1].replace('_', ' ')
            try:
                if '[' in pair[1] or '(' in pair[1]:
                    pair[1] = list(pair[1])
                elif '.' in pair[1]:
                    pair[1] = float(pair[1])
                else:
                    pair[1] = eval(pair[1])
                #pair[1] = eval(pair[1])
            except Exception:
                pass
        return dict(pairs)

if __name__ == "__main__":
    '''
        Entry point for the loop.
    '''
    DockerHeartsCommand().cmdloop()