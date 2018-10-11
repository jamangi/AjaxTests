#!/usr/bin/python3
from flask import Flask, request, jsonify
from flask_cors import CORS
from fundamentals import create_file
from nest import test_file

app = Flask(__name__)
app.url_map.strict_slashes = False
cors = CORS(app, resources={r"/*": {"origins": "0.0.0.0"}})


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
    app.run(host='0.0.0.0', port=9000)
