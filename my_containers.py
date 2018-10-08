#!/usr/bin/python3
from flask import Flask, request, jsonify
import docker
import uuid
import subprocess

from fundamentals import create_file, copy_file, execute_file, extract_heart

app = Flask(__name__)

client = docker.from_env()
def test_file(file_obj):
    """ Copy file into container, execute file in container, return output """
    testtube = client.containers.run('rubyshadows/heartbeat:v1', detach=True) 

    c_name = testtube.name
    print()
    print("testtube name: {}".format(c_name))
    file_id = file_obj['id']
    file_name = file_obj['filename']
    file_type = file_obj['filetype']

    copy_good = copy_file(c_name, file_id, file_name)
    if copy_good:
        status = "success"
    else:
        status = "failure"
    print("copy file {} inside container {} - {}".format(file_name, c_name, status))
    exec_good = execute_file(c_name, file_name, file_type)
    print()

    if exec_good:
        status = "success"
    else:
        status = "failure"
    print("execute {} {} inside of container {} - {}".format(file_type, file_name, c_name, status))
    print()

    responding = check_container(c_name)
    if responding:
        status = "responding"
    else:
        status = "not responding"
    print("container is {}".format(status))

    if responding:
        has_heart = extract_heart(c_name)
    else:
        has_heart = None

    print("container heart: {}".format(has_heart))

    material = 0

    if "python" in file_type:
        material = 6
    elif "bash" in file_type:
        material = 2

    if exec_good:
        if (not has_heart) or (not responding):
            material *= 10
    else:
        material = 0

    print("material value: {}".format(material))

    testtube.remove(force=True)

    return material

def check_container(container_name):
    """ Checks whether container is running """
    container = client.containers.get(container_name)
    if container.status == "running":
        return True
    else:
        return False


@app.route('/')
def hello():
    return "hi"

@app.route('/drop', methods=["POST"])
def drop():
    filename = request.json['filename']
    text = request.json['filetext']
    user_id = request.remote_addr
    file_obj = create_file(user_id, filename, text)
    print("""filename: {}\nfiletext: {}\nuser_ip: {}
           file_obj: {}""".format(filename, text, user_id, file_obj))
    material = test_file(file_obj)
    return jsonify({"material":material})


app.run(host='0.0.0.0', port=9090)
