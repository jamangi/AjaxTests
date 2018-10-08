#!/usr/bin/python3
from flask import Flask, request, jsonify
import docker
import uuid
import subprocess

from fundamentals import copy_file, execute_file, extract_heart

app = Flask(__name__)

client = docker.from_env()
def test_file(file_obj):
    """ Copy file into container, execute file in container, return output """
    testtube = client.containers.run('rubyshadows/heartbeat:v1', detach=True) 

    c_name = testtube.name
    file_id = file_obj['uid']
    file_name = file_obj['filename']
    file_type = file_obj['filetype']

    copy_file(c_name, file_id, filename)
    execute_file(c_name, filename, filetype)
    responding = check_container(c_name)
    if responding:
        has_heart = extract_heart(c_name)
    else
        has_heart = None

    return (responding, has_heart)

def check_container(container_name):
    """ Checks whether container is running """
    container = client.containers.get(container_name)
    if container.status == "running":
        return True
    else:
        return False

def run():
    client = docker.from_env()
    output = client.containers.run('alpine', 'echo hello world');
    print(output)

@app.route('/')
def hello():
    #run()
    return "hi"

@app.route('/drop', methods=["POST"])
def drop():
    filename = request.json['filename']
    text = request.json['text']
    user_id = request.remote_addr
    file_obj = create_file(user_id, filename, text)
    run_as = "testtube"
    responding, has_heart = test_file(file_obj, filename)
    return jsonify({"output": output, "hasHeart":responding and has_heart})


app.run(host='0.0.0.0', port=9090)
