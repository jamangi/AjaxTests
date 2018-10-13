import docker

from fundamentals import copy_file, execute_file, extract_heart

client = docker.from_env()
NEST = {}


def load_container(user_id):
    '''
        TODO: Pull container from dockerhub and return it
        If none on dockerhub, create new one
    '''
    container = NEST.get(user_id)
    if container is None:
        return new_container(user_id)
    else:
        return container

def new_container(user_id):
    '''
        Remove old container and create new one
    '''
    remove_container(user_id)
    container = client.containers.run('rubyshadows/heartbeat:v1', detach=True) 
    NEST[user_id] = container
    return container

def user_container(user_id):
    '''
        Finds running container on machine and returns it
    '''
    return NEST.get(user_id)

def remove_container(user_id):
    '''
        Remove container from memory
    '''
    container = NEST.get(user_id)
    if container == None:
        return
    else:
        container.remove(force=True)
    del NEST[user_id]

def run_file(user_id, file_obj):
    '''
        Run a file within container, return output and hasHeart
    '''
    c_name = NEST.get(user_id).name
    print()
    print("User {}: {}".format(user_id, c_name))
    file_id = file_obj['fileid']
    file_name = file_obj['filename']
    file_type = file_obj['filetype']

    copy_good = copy_file(c_name, file_id, file_name)
    output = execute_file(c_name, file_name, file_type)
    responding = check_container(c_name)
    if responding:
        has_heart = extract_heart(c_name)
    else:
        has_heart = None

    print("Heart: {}\n".format(has_heart))
    return {"output": output, "has_heart": has_heart}


def test_file(file_obj):
    """ Copy file into container, execute file in container, return output """
    testtube = client.containers.run('rubyshadows/heartbeat:v1', detach=True) 

    c_name = testtube.name
    print()
    print("testtube name: {}".format(c_name))
    file_id = file_obj['fileid']
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
