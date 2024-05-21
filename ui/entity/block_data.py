class BlockingData(object):

    def __init__(self):
        self._test_control_type = ''
        self._test_control = ''
        self._ios_control_type = ''
        self._ios_control = ''

    @property
    def test_control_type(self):
        return self._test_control_type

    @test_control_type.setter
    def test_control_type(self, value):
        self._test_control_type = value

    @property
    def test_control(self):
        return self._test_control

    @test_control.setter
    def test_control(self, value):
        self._test_control = value

    @property
    def ios_control_type(self):
        return self._ios_control_type

    @ios_control_type.setter
    def ios_control_type(self, value):
        self._ios_control_type = value

    @property
    def ios_control(self):
        return self._ios_control

    @ios_control.setter
    def ios_control(self, value):
        self._ios_control = value