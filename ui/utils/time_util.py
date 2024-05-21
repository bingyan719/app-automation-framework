import time

def get_now_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

def sleep(seconds):
    time.sleep(seconds)