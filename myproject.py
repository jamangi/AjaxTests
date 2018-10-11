#!/usr/bin/python3
from flask import Flask, request, jsonify
from flask_cors import CORS

import db
from fundamentals import create_file
from nest import test_file

app = Flask(__name__)
app.url_map.strict_slashes = False
cors = CORS(app, resources={r"/*": {"origins": "0.0.0.0"}})


@app.route('/')
def hello():
    return "hi"

@app.route('/connect')
def connect():
    ''' Search for ip in database '''
    user_ip = request.remote_addr
    user = db.get_user_by_ip(user_ip)
    if user is None:
        return jsonify({})
    else:
        return jsonify(user.to_dict())

@app.route('/set', methods=["POST"])
def set_user():
    ''' Set username and doggy type of ip, adds ip if not found '''
    requires = ["name", "character"]
    for req in requires:
        if req not in request.json:
            return jsonify({"msg": "no {}".format(req)})

    user_ip = request.remote_addr
    name = request.json["name"]
    character = request.json["character"]
    user = db.get_user_by_ip(user_ip)
    if user is None:
        user = db.create("User", ip=user_ip, name=name, character=character) 
    else:
        user = db.update(ip, name=name, character=character)

    if user is None:
        return jsonify({})
    else:
        return jsonify(user.to_dict())

@app.route('/collect', methods=["POST"])
def collect():
    ''' Execute inside user container and update database '''
    return "collect"

@app.route('/drop', methods=["POST"])
def drop():
    ''' Test file and save it to database '''
    return "drop"


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
    app.run(host='0.0.0.0', port=9000)
