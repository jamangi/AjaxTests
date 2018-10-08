import subprocess
import uuid

def copy_file(container_name, file_id, filename):
    """ will error if home directory is missing """
    try:
        return subprocess.check_output(["docker","cp","work/{}".format(file_id),
                                 "{}:/home/{}".format(container_name, filename)])
    except Exception as e:
        return None

def extract_heart(container_name):
    try:
        return subprocess.check_output(["docker","cp","{}:/home/heart".format(container_name),
                                        "heartdump.txt"])
    except Exception as e:
        return None


def execute_file(container_name, filename, filetype):
    try:
        output = subprocess.check_output(["docker", "exec", container_name, filetype, "/home/{}".format(filename)])
        return output
    except Exception as e:
        return None

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

def create_file(user_id, filename, text):
    """ Create file in staging direcory """
    uid = str(uuid.uuid4())
    new_file = {"id": uid, "user_id":user_id,
                "filename": filename, "text": text,
                "filetype": read_shebang(text)}
    with open("work/{}".format(new_file["id"]), mode="a", encoding="utf-8") as fd:
        lines = text.splitlines()
        for line in lines:
            print(line, file=fd)
    return new_file
