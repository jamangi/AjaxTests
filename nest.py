import docker

import db
import fundamentals

client = docker.from_env()
NEST = {}

def save_container(user_id, container):
    '''
        Commit and save container to dockerhub
    '''
    user = db.get("User", user_id)
    
    if user is None:
        return None

    if container is None:
        return None

    user.container_version += 1
    db.save()

    repo = "rubyshadows/{}".format(user_id)
    container.commit(repository=repo,
                     author=user.name,
                     tag=user.container_version)
    print("saving container: {}".format(user_id))
    # client.images.push(repo)
    fundamentals.push_image(user_id, user.container_version)
    return True

def load_container(user_id, version=None):
    '''
        TODO: Pull container from dockerhub and return it
        If none on dockerhub, create new one
    '''
    user = db.get("User", user_id)
    if user is None:
        return None

    remove_container(user_id)
    repo = "rubyshadows/{}".format(user_id)
    if version is None:
        version = user.container_version
    full = "{}:{}".format(repo, version)
    try:
        print("pulling image from repo")
        img = client.images.pull(repo, tag=str(version))
        print("client.images.pull: {}".format(img))
        container = client.containers.run(full, detach=True)
        NEST[user_id] = container
        print("successful pull: {}".format(user_id))
        return container
    except (docker.errors.ImageNotFound, docker.errors.APIError) as e:
        print("remote image not found: {}".format(full))
        print(e)
        print("creating new container\n")
        return new_container(user_id)


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
        del NEST[user_id]
        save_container(user_Id, container)
        container.remove(force=True)

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

    copy_good = fundamentals.copy_file(c_name, file_id, file_name)
    output = fundamentals.execute_file(c_name, file_name, file_type)
    responding = check_container(c_name)
    if responding:
        has_heart = fundamentals.extract_heart(c_name)
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

    copy_good = fundamentals.copy_file(c_name, file_id, file_name)
    if copy_good:
        status = "success"
    else:
        status = "failure"
    print("copy file {} inside container {} - {}".format(file_name, c_name, status))
    exec_good = fundamentals.execute_file(c_name, file_name, file_type)
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
        has_heart = fundamentals.extract_heart(c_name)
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
