import sys

from ui.utils.time_util import get_now_time

class colour:
    @staticmethod
    def c(msg, colour):
        try:
            from termcolor import colored, cprint
            p = lambda x: cprint(x, '%s' % colour)
            return p(msg)
        except:
            print(msg)

    @staticmethod
    def show_verbose(msg):
        colour.c(msg, 'white')

    @staticmethod
    def show_debug(msg):
        colour.c(msg, 'blue')

    @staticmethod
    def show_info(msg):
        colour.c(msg, 'green')

    @staticmethod
    def show_warn(msg):
        colour.c(msg, 'yellow')

    @staticmethod
    def show_error(msg):
        colour.c(msg, 'red')


class Logging:
    flag = True

    @staticmethod
    def error(msg):
        if Logging.flag:
            colour.show_error(get_now_time() + " [Error]: " + "".join(msg))

    @staticmethod
    def warn(msg):
        if Logging.flag:
            colour.show_warn(get_now_time() + " [Warn]: " + "".join(msg))

    @staticmethod
    def info(msg):
        if Logging.flag:
            colour.show_info(get_now_time() + " [Info]: " + "".join(msg))

    @staticmethod
    def debug(msg):
        if Logging.flag:
            colour.show_debug(get_now_time() + " [Debug]: " + "".join(msg))

    @staticmethod
    def success(msg):
        if Logging.flag:
            colour.show_verbose(get_now_time() + " [Success]: " + "".join(msg))


def print_log():
    def log(func):
        def wrapper(*args, **kwargs):
            t = func(*args, **kwargs)
            filename = str(sys.argv[0]).split('/')[-1].split('.')[0]
            Logging.success('{}:{}, return:{}'.format(filename, func.__name__, t))
            return t

        return wrapper

    return log


class Logs(object):
    
    def __init__(self, type, message):
        self._type = type
        self._message = message
        self._time = get_now_time()

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value