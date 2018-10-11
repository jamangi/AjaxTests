import subprocess
import uuid

def copy_file(container_name, file_id, filename):
    """ will error if home directory is missing """
    try:
        subprocess.check_output(["docker","cp","work/{}".format(file_id),
                                 "{}:/home/{}".format(container_name, filename)])
        return True
    except Exception as e:
        print("Error in copy: {}".format(e))
        return None

def extract_heart(container_name):
    try:
        output = subprocess.check_output(["docker","cp","{}:/home/heart".format(container_name),
                                          "heartdump.txt"])
        return True
    except Exception as e:
        return None


def execute_file(container_name, filename, filetype):
    try:
        output = subprocess.check_output(["docker", "exec", container_name, filetype, "/home/{}".format(filename)])
        if output:
            return output
        else:
            return True
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

def create_file(user_ip, filename, text, row, col):
    """ Create file in staging direcory """
    uid = str(uuid.uuid4())
    new_file = {"file_id": uid, "user_ip":user_ip,
                "filename": filename, "text": text,
                "filetype": read_shebang(text),
                "row": row,
                "col": col}
    with open("work/{}".format(new_file["file_id"]), mode="a", encoding="utf-8") as fd:
        lines = text.splitlines()
        for line in lines:
            print(line, file=fd)
    return new_file
