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
        user.touch()
        container = nest.user_container(user.id)
        if container is None:
            return jsonify({"msg": "no container"})
        ret = user.to_dict()
        del ret["ip"]
        return jsonify({"user":ret, "container_name": container.name})

@app.route('/touch')
def touch():
    ''' Send alive signal '''
    user_ip = request.remote_addr
    user = db.get_user_by_ip(user_ip)
    if user is None:
        return jsonify({"msg": "no user"})
    else:
        user.touch()
        ret = user.to_dict()
        del ret["ip"]
        return jsonify({"user": ret})

@app.route('/set', methods=["POST"])
def set_user():
    ''' Set username and doggy type of ip, adds ip if not found '''
    requires = ["name", "character", "location"]
    if not request.json:
        return jsonify({"msg": "not json"}), 400
    for req in requires:
        if not request.json.get(req):
            return jsonify({"msg": "no {}".format(req)}), 400

    user_ip = request.remote_addr
    name = request.json["name"]
    character = request.json["character"]
    location = request.json["location"]
    user = db.get_user_by_ip(user_ip)
    if user is None:
        user = db.create("User", ip=user_ip, name=name,
                         character=character,
                         form=character, location=location) 
    else:
        user = db.update(user_ip, name=name,
                         character=character,
                         form=character, location=location) 

    user.touch()
    if user is None:
        return jsonify({})
    else:
        ret = user.to_dict()
        del ret["ip"]
        return jsonify({"user": ret})

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
    if script is None:
        return jsonify({"msg":"script not found"})

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
   

    container = nest.load_container(user.id)
    file_obj = create_file(user_ip, filename, text, row, col)
    result = nest.run_file(user.id, file_obj)
    result['filename'] = filename;
    result['filetext'] = text;

    if result["has_heart"] == None or result["has_heart"] == False:
        user.form = 'ghost'
        if is_bad_file:
            author.add_material(user.pay_material(script.material))
    else:
        user.form = user.character
        script.collect(user.id)
        if is_bad_file:
            user.add_material(script.material)
        else:
            user.add_material(script.material)
            author.add_material(script.material)

    db.save()
    ret = user.to_dict()
    del ret["ip"]
    return jsonify({"result": result, "user": ret})

@app.route('/drop', methods=["POST"])
def drop():
    ''' Test file and save it to database '''
    user_ip = request.remote_addr
    user = db.get_user_by_ip(user_ip) 
    if user is None:
        return jsonify({"msg": "ip not set"}), 401
    user.touch()

    requires = ["filename", "filetext", "row", "col"];
    if not request.json:
        return jsonify({"msg": "not json"}), 400
    for req in requires:
        if not request.json.get(req):
            return jsonify({"msg": "no {}".format(req)}), 400

    filename = request.json['filename']
    text = request.json['filetext']
    row = request.json['row']
    col = request.json['col']
    
    if user.form == 'ghost':
        return jsonify({"msg": "you're a ghost"})

    user.material += 1;
    file_obj = create_file(user_ip, filename, text, row, col)
    material = nest.test_file(file_obj)
    
    new_file = db.create("Script", user_id=user.id, material=material,
              filename=filename, filetext=text, filetype=file_obj['filetype'],
              row=row, col=col, location=user.location)
    db.save()
    res = user.to_dict()
    del res['ip']
    script = new_file.to_dict()
    script['user'] = res
    return jsonify({"script" : script, "user": res})

@app.route('/dump', methods = ["POST"])
def dump_scripts():
    '''
        Upload script from file
    '''
    user_ip = request.remote_addr
    user = db.get_user_by_ip(user_ip) 
    if user is None:
        return jsonify({"msg": "ip not set"}), 401
    user.touch()

    f = request.files['file']
    filename = f.filename
    row = 0
    col = 0
    text = f.read().decode("utf-8")

    if user.form == 'ghost':
        return jsonify({"msg": "you're a ghost"})


    user.material += 1;
    file_obj = create_file(user_ip, filename, text, row, col)
    material = nest.test_file(file_obj)
    
    new_file = db.create("Script", user_id=user.id, material=material,
              filename=filename, filetext=text, filetype=file_obj['filetype'],
              row=row, col=col, location=user.location)
    db.save()
    res = user.to_dict()
    del res['ip']
    script = new_file.to_dict()
    script['user'] = res
    return jsonify({"script" : script, "user": res})

@app.route('/edit', methods=["POST"])
def edit():
    '''
        Edit a dropped script
    '''
    requires = ["fileid", "filename", "filetext"]
    user_ip = request.remote_addr
    user = db.get_user_by_ip(user_ip)
    if user is None:
        return jsonify({"msg": "ip not set"}), 401

    user.touch()
    if not request.json:
        return jsonify({"msg": "not json"}), 400

    for req in requires:
        if not request.json.get(req):
            return jsonify({"msg": "no {}".format(req)}), 400

    script = db.get("Script", fileid)
    if script is None:
        return jsonify({"msg":"script not found"})
    author = db.get("User", script.user_id)
    if author.id != user.id:
        return jsonify({"msg": "script is not yours"})

    filename = request.json.get("filename")
    text = request.json.get("filetext")
    row = script.row
    col = script.col

    file_obj = create_file(user_ip, filename, text, row, col)
    material = nest.test_file(file_obj)

    script.filename = filename
    script.filetext = text
    script.material = material

    db.save()
    res = user.to_dict()
    del res['ip']
    script = new_file.to_dict()
    script['user'] = res
    return jsonify({"script" : script, "user": res})

#TODO: @app.route('/backup')

@app.route('/full_restore')
def full_restore():
    '''
        Replace user container
    '''
    user_ip = request.remote_addr
    user = db.get_user_by_ip(user_ip)
    if user is None:
        return jsonify({"msg": "ip not set"}), 401
    nest.remove_container(user.id)
    container = nest.new_container(user.id)
    user.form = user.character
    db.save()
    user.touch()
    ret = user.to_dict()
    del ret["ip"]
    return jsonify({"user": ret, "container_name":container.name})

@app.route('/heal')
def heal():
    '''
        Puts heart file into user's container
    '''
    user_ip = request.remote_addr
    user = db.get_user_by_ip(user_ip)
    if user is None:
        return jsonify({"msg": "ip not set"}), 401

    container = nest.user_container(user.id)
    if container == None:
        container = nest.new_container(user.id)
    has_heart = nest.heal_container(container)
    if has_heart == False:
        user.form = 'ghost'
    elif has_heart == None:
        user.form = user.form
    else:
        user.form = user.character
    db.save()
    user.touch()
    ret = user.to_dict()
    del ret["ip"]
    return jsonify({"user": ret})

@app.route('/load')
@app.route('/load/<location>')
def load_scripts(location=None):
    '''
        Loads scripts from memory
    '''
    all_scripts = []
    for script in db.get_scripts(location):
        s = script.to_dict()
        user = db.get("User", script.user_id)
        ret = user.to_dict();
        del ret['ip']
        s["user"] = ret
        all_scripts.append(s)
    return jsonify({"scripts": all_scripts})


@app.route('/run', methods=["POST"])
def run_script():
    '''
        Run's script inside own container
    '''
    requires = ["filename", "filetext"]
    if not request.json:
        return jsonify({"msg": "not json"}), 400
    for req in requires:
        if not request.json.get(req):
            return jsonify({"msg": "no {}".format(req)}), 400
    filename = request.json['filename']
    text = request.json['filetext']
    row = 0
    col = 0
    user_ip = request.remote_addr
    
    user = db.get_user_by_ip(user_ip) 
    if user is None:
        return jsonify({"msg": "ip not set"}), 401
    
    user.touch()
    container = nest.load_container(user.id)
    file_obj = create_file(user_ip, filename, text, row, col)
    result = nest.run_file(user.id, file_obj)
    result['filename'] = filename;
    result['filetext'] = text;

    if result["has_heart"] == False:
        user.form = 'ghost'
    elif result["has_heart"] == None:
        user.form = user.form
    else:
        user.form = user.character

    db.save()
    ret = user.to_dict()
    del ret["ip"]
    return jsonify({"result": result, "user": ret})


@app.route('/start')
def start():
    '''
        Creates user container
    '''
    # search database for ip:id
    user_ip = request.remote_addr
    user = db.get_user_by_ip(user_ip)
    if user is None:
        return jsonify({"msg": "ip not set"}), 401

    container = nest.load_container(user.id)
    user.touch()

    ret = user.to_dict()
    del ret["ip"]
    return jsonify({"user": ret, "container_name":container.name})

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
    return jsonify({"material":material})


    

@app.after_request
def handle_cors(response):
    # allow access from other domains
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
