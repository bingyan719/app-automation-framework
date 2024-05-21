from six import with_metaclass


class MetaDevice(type):

    REGISTRY = {}

    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        meta.REGISTRY[name] = cls
        return cls


class Device(with_metaclass(MetaDevice, object)):
    """base class for test device"""

    def __init__(self):
        super(Device, self).__init__()

    @property
    def uuid(self):
        self._raise_not_implemented_error()

    def install_app(self, uri, **kwargs):
        self._raise_not_implemented_error()

    def uninstall_app(self, package):
        self._raise_not_implemented_error()

    def start_app(self, package, **kwargs):
        self._raise_not_implemented_error()

    def stop_app(self, package):
        self._raise_not_implemented_error()

    def clear_app(self, package):
        self._raise_not_implemented_error()

    def current_activity(self):
        self._raise_not_implemented_error()

    def home(self):
        self._raise_not_implemented_error()

    def tap(self, x, y):
        self._raise_not_implemented_error()

    def click(self, locator, wait=2, runWatcher=True):
        self._raise_not_implemented_error()

    def longclick(self, locator, wait=2, runWatcher=True):
        self._raise_not_implemented_error()
    
    def wait_until(self, locator, times=15):
        self._raise_not_implemented_error()

    def swipe_until(self, direction, locator, timeout=10):
        self._raise_not_implemented_error()

    def text(self, locator, content, **kwargs):
        self._raise_not_implemented_error()

    def exists(self, locator, wait=15):
        self._raise_not_implemented_error()
    
    def find_element(self, locator, wait=15):
        self._raise_not_implemented_error()

    def screenshot(self, filename):
        self._raise_not_implemented_error()

    def run_watcher(self):
        self._raise_not_implemented_error()
    
    def swipe(self, startX, startY, endX, endY):
        self._raise_not_implemented_error()

    def swipe_left_full(self):
        self._raise_not_implemented_error()

    def _raise_not_implemented_error(self):
        platform = self.__class__.__name__
        raise NotImplementedError("Method not implemented on %s" % platform)