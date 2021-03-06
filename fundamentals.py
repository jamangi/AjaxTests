import subprocess
import uuid

def push_image(user_id, ver):
    '''
        Push repo to docker hub
    '''
    try:
        repo = "rubyshadows/{}:{}".format(user_id, ver)
        subprocess.check_output(["sudo", "docker","push", repo])
        print("pushed: {}".format(repo))
        return True
    except Exception as e:
        print("Error in image push: {}".format(e))
        return None

def pull_image(user_id, ver):
    '''
        Pull image from docker hub
    '''
    try:
        repo = "rubyshadows/{}:{}".format(user_id, ver)
        subprocess.check_output(["sudo", "docker","pull", repo])
        print("pulled: {}".format(repo))
        return True
    except Exception as e:
        print("Error in image pull: {}".format(e))
        return None

def copy_file(container_name, fileid, filename):
    """ will error if home directory is missing """
    try:
        subprocess.check_output(["sudo", "docker","cp","work/{}".format(fileid),
                                 "{}:/home/{}".format(container_name, filename)])
        return True
    except Exception as e:
        print("Error in copy: {}".format(e))
        return None

def execute_file(container_name, filename, filetype):
    '''
        Execute file within container
    '''
    try:
        output = subprocess.check_output(["sudo", "docker", "exec", container_name, filetype, "/home/{}".format(filename)])
        if output:
            return output
        else:
            return False
    except Exception as e:
        return None

def extract_heart(container_name):
    '''
        Searches for heart file in container.
        TODO: make error catch more specific
    '''
    try:
        output = subprocess.check_output(["sudo", "docker","cp","{}:/home/heart".format(container_name),
                                          "heartdump.txt"])
        return True
    except Exception as e:
        return False

def read_shebang(text):
    """ Read shebang and deduce programming language """
    lines = text.splitlines()
    if lines[0][0] == "#":
        comment = lines[0]
        interpreter = ''
        for i in range(len(comment)-1, -1, -1):
            if comment[i] == ' ' or comment[i] == '/':
                break
            interpreter = comment[i] + interpreter
        return interpreter
    else:
        return 'bash'

def create_file(user_ip, filename, text, row, col):
    """ Create file in staging direcory """
    uid = str(uuid.uuid4())
    new_file = {"fileid": uid, "user_ip":user_ip,
                "filename": filename, "text": text,
                "filetype": read_shebang(text),
                "row": row,
                "col": col}
    with open("work/{}".format(new_file["fileid"]), mode="a", encoding="utf-8") as fd:
        lines = text.splitlines()
        for line in lines:
            print(line, file=fd)
    return new_file
