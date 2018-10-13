#!/usr/bin/python3
import atexit
from flask import Flask, request, jsonify
from flask_cors import CORS

import db
import cleanup
from fundamentals import create_file
import nest

app = Flask(__name__)
app.url_map.strict_slashes = False
cors = CORS(app, resources={r"/*": {"origins": "0.0.0.0"}})
cleanup.start_cleaner()

@app.route('/')
def status():
    '''
        Status check
    '''
    return jsonify({"status": "ok"})

@app.route('/check')
def check_container():
    '''
        checks if container exists for this user
    '''
    user_ip = request.remote_addr
    user = db.get_user_by_ip(user_ip)
    if user is None:
        return jsonify({"msg": "no user"})
    else:
        container = nest.user_container(user.id)
        if container is None:
            return jsonify({"msg": "no container"})

        return jsonify({"container_name": container.name})

@app.route('/connect')
def connect():
    ''' Search for ip in database '''
    user_ip = request.remote_addr
    user = db.get_user_by_ip(user_ip)
    if user is None:
        return jsonify({})
    else:
        user.touch()
        ret = user.to_dict()
        del ret["ip"]
        return jsonify(ret)

@app.route('/set', methods=["POST"])
def set_user():
    ''' Set username and doggy type of ip, adds ip if not found '''
    requires = ["name", "character", "base_form", "location"]
    if not request.json:
        return jsonify({"msg": "not json"}), 400
    for req in requires:
        if not request.json.get(req):
            return jsonify({"msg": "no {}".format(req)}), 400

    user_ip = request.remote_addr
    name = request.json["name"]
    character = request.json["character"]
    base_form = request.json["base_form"]
    location = request.json["location"]
    user = db.get_user_by_ip(user_ip)
    if user is None:
        user = db.create("User", ip=user_ip, name=name,
                         character=character, base_form=base_form,
                         form=base_form, location=location) 
    else:
        user = db.update(user_ip, name=name,
                         character=character, base_form=base_form,
                         form=base_form, location=location) 

    user.touch()
    if user is None:
        return jsonify({})
    else:
        ret = user.to_dict()
        del ret["ip"]
        return jsonify(ret)

@app.route('/collect', methods=["POST"])
def collect():
    ''' Execute inside user container and update database '''
    requires = ["fileid"]
    if not request.json:
        return jsonify({"msg": "not json"}), 400
    for req in requires:
        if not request.json.get(req):
            return jsonify({"msg": "no {}".format(req)}), 400
    fileid = request.json['fileid']
    user_ip = request.remote_addr
    user = db.get_user_by_ip(user_ip)
    if user is None:
        return jsonify({"msg": "ip switched"})

    user.touch()

    if user.form == 'ghost':
        return jsonify({"msg": "you're a ghost"})

    script = db.get("Script", fileid)
    filename = script.filename
    text = script.filetext
    row = script.row
    col = script.col
    is_bad_file = script.material >= 20
    author = db.get("User", script.user_id)
    if author.id == user.id:
        return jsonify({"msg": "script is yours"})

    if script.has_collected(user.id):
        return jsonify({"msg": "you've already collected this script"})

    if user.has_space() == False:
        return jsonify({"msg": "bag is full"})    

    container = nest.load_container(user.id)
    file_obj = create_file(user_ip, filename, text, row, col)
    result = nest.run_file(user.id, file_obj)

    if result["has_heart"] == None or result["has_heart"] == False:
        user.form = 'ghost'
        if is_bad_file:
            author.add_material(user.pay_material(script.material))
    else:
        user.form = user.base_form
        script.collect(user.id)
        user.add_script()
        if is_bad_file:
            user.add_material(script.material)
        else:
            user.add_material(script.material)
            author.add_material(script.material)

    db.save()
    return jsonify(result)

@app.route('/drop', methods=["POST"])
def drop():
    ''' Test file and save it to database '''
    requires = ["filename", "filetext"]
    if not request.json:
        return jsonify({"msg": "not json"}), 400
    for req in requires:
        if not request.json.get(req):
            return jsonify({"msg": "no {}".format(req)}), 400
    filename = request.json['filename']
    text = request.json['filetext']
    row = request.json['row']
    col = request.json['col']
    user_ip = request.remote_addr
    
    user = db.get_user_by_ip(user_ip) 
    if user is None:
        return jsonify({"msg": "ip switched"})
    
    user.touch()
    if user.form == 'ghost':
        return jsonify({"msg": "you're a ghost"})

    if user.use_script() is None:
        return jsonify({"msg": "bag is empty"})
    file_obj = create_file(user_ip, filename, text, row, col)
    material = nest.test_file(file_obj)
    
    new_file = db.create("Script", user_id=user.id, material=material,
              filename=filename, filetext=text, filetype=file_obj['filetype'],
              row=row, col=col, location=user.location)
    db.save()
    res = user.to_dict()
    del res['ip']
    return jsonify({"user": res, "script" : new_file.to_dict()})

#TODO: @app.route('/backup')

@app.route('/full_restore')
def full_restore():
    '''
        Replace user container
    '''
    user_ip = request.remote_addr
    user = db.get_user_by_ip(user_ip)
    if user is None:
        return jsonify({"msg": "ip not found"})
    nest.remove_container(user.id)
    container = nest.new_container(user.id)
    user.form = user.base_form
    db.save()
    user.touch()
    return jsonify({"container_name":container.name})

@app.route('/heal')
def heal():
    '''
        Puts heart file into user's container
    '''
    user_ip = request.remote_addr
    user = db.get_user_by_ip(user_ip)
    if user is None:
        return jsonify({"msg": "ip not found"})
    container = nest.load_container(user.id)

    filename = "heart"
    text = ";)" #TODO: change to random quote
    row = 0
    col = 0

    file_obj = create_file(user_ip, filename, text, row, col)
    result = nest.run_file(user.id, file_obj)
    if result["has_heart"] == None or result["has_heart"] == False:
        user.form = 'ghost'
    else:
        user.form = user.base_form
    db.save()
    user.touch()
    return jsonify(result)

@app.route('/start')
def start():
    '''
        Creates user container
    '''
    # search database for ip:id
    user_ip = request.remote_addr
    user = db.get_user_by_ip(user_ip)
    if user is None:
        return jsonify({"msg": "ip not found"})

    container = nest.load_container(user.id)
    user.touch()

    return jsonify({"container_name":container.name})

@app.route('/test', methods=["POST"])
def test():
    requires = ["filename", "filetext"]
    if not request.json:
        return jsonify({"msg": "not json"}), 400
    for req in requires:
        if not request.json.get(req):
            return jsonify({"msg": "no {}".format(req)}), 400
    print(request.json)
    filename = request.json['filename']
    text = request.json['filetext']
    row = request.json['row']
    col = request.json['col']
    user_ip = request.remote_addr
    file_obj = create_file(user_ip, filename, text, row, col)
    print("filename: {}\nfiletext: {}\nuser_ip: {} file_obj: {}".format(filename, 
                                                                        text, 
                                                                        user_ip, 
                                                                        file_obj))
    material = nest.test_file(file_obj)
    return jsonify({"material":material, "fileid":file_obj['fileid']})


@app.after_request
def handle_cors(response):
    # allow access from other domains
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
