#!/usr/bin/python3
from flask import Flask, request, jsonify
import docker

app = Flask(__name__)

def make_filename(user_id, filename):
    """ file naming convension """
    return "{}~{}".format(user_id, filename)

def create_file(user_id, filename, text):
    """ Create file in staging direcory """
    pass

def read_shebang(filename):
    """ Read shebang and deduce programming language """
    pass

def exec_file(user_id, filename):
    """ Copy file into container, execute file in container, return output """
    return ("123", "cats\ndogs\npies")

def check_container(container_id):
    """ Checks whether container is healthy """
    return (True, True)

def run():
    client = docker.from_env()
    output = client.containers.run('alpine', 'echo hello world');
    print(output)

@app.route('/')
def hello():
    run()
    return "hi"

@app.route('/collect', methods=["POST"])
def collect():
    filename = request.json['scriptname']
    text = request.json['scripttext']
    user_id = request.remote_addr
    create_file(user_id, filename, text)
    container_id, output = exec_file(user_id, filename)
    responding, has_heart = check_container(container_id)
    return jsonify({"output": output, "hasHeart":responding and has_heart})


app.run(host='0.0.0.0', port=9090)
