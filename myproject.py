#!/usr/bin/python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import docker
import uuid
import subprocess

from fundamentals import create_file, copy_file, execute_file, extract_heart

app = Flask(__name__)
app.url_map.strict_slashes = False
cors = CORS(app, resources={r"/*": {"origins": "0.0.0.0"}})
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
    else:
        material = 10

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

@app.route('/test', methods=["POST"])
def test():
    if "filename" not in request.json:
        return jsonify({"msg": "no filename"})
    print(request.json)
    filename = request.json['filename']
    text = request.json['filetext']
    row = request.json['row']
    col = request.json['col']
    user_id = request.remote_addr
    file_obj = create_file(user_id, filename, text, row, col)
    print("filename: {}\nfiletext: {}\nuser_ip: {} file_obj: {}".format(filename, 
                                                                        text, 
                                                                        user_id, 
                                                                        file_obj))
    material = test_file(file_obj)
    return jsonify({"material":material, "file_id":file_obj['id']})


@app.after_request
def handle_cors(response):
    # allow access from other domains
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
