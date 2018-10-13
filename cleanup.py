import atexit
import datetime
from threading import Timer

import nest
import db

seconds_till_scan = 10
seconds_till_inactive = 20
inactive = []
x = datetime.datetime(1, 1, 1, second=seconds_till_inactive)
y = datetime.datetime(1, 1, 1, second=0)
threshold = x - y

def scan_for_inactive():
    '''
        Marks inactive containers based on user.updated_at.
        Nest provides user_id : container
        So it checks datetime.now() - user.updated_at
            and either pushes container to inactive or not
    '''
    print("performing inactivity scan")
    global threshold
    global inactive
    for user_id, container in nest.NEST.items():
        user = db.get("User", user_id)
        updated_at = user.updated_at
        now = datetime.datetime.now()
        afk_time = now - updated_at
        if afk_time > threshold:
            inactive.append(container)
            print("inactive container: {}".format(user.ip))
        else:
            print("active container: {}".format(user.ip))

def remove_all():
    '''
        Remove all containers
        TODO: use nest.remove, to ensure its pushed to dockerhub
    '''
    for user_id, container in nest.NEST.items():
        nest.remove_container(user_id)

def remove_inactive():
    '''
        Removes all inactive containers using nest.remove
            also pops container from list
    '''
    global inactive
    count = len(inactive)
    while count:
        count -= 1
        container = inactive.pop()
        print("Removing container: {}".format(container.name))
        container.remove(force=True)

def make_pass(*args, **kwargs):
    '''
        Scans and removes
    '''
    scan_for_inactive()
    remove_inactive()

class RepeatedTimer(object):
    '''
        https://stackoverflow.com/questions/3393612/run-certain-code-every-n-seconds
        Object to scan inactive for containers every interval
    '''
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

def start_cleaner():
    '''
        Starts cleanup loop
    '''
    global cleaner
    cleaner.start()

def stop_cleaner():
    '''
        Stops cleanup loop
    '''
    global cleaner
    cleaner.stop()

cleaner = RepeatedTimer(seconds_till_scan, make_pass)
atexit.register(stop_cleaner)
atexit.register(remove_all)
