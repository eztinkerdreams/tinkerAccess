import os

tmp_file = '/tmp/login.txt'


class _VirtualSerial(object):
    def __init__(self, *args):
        self.__badge_code = None

    # noinspection PyPep8Naming
    def flushInput(self, *args):
        if os.path.isfile(tmp_file):
            os.remove(tmp_file)
            self.__badge_code = None

    # noinspection PyPep8Naming
    def flushOutput(self, *args):
        pass

    def inWaiting(self, *args):
        self.__read_line()
        return len(self.__badge_code) if self.__badge_code is not None else 0

    def readline(self, *args):
        return self.__badge_code

    # noinspection PyMethodMayBeStatic
    def __read_line(self):
        if os.path.isfile(tmp_file):
            with open(tmp_file, 'r') as f:
                badge_code = f.readline()
                if len(badge_code):
                    self.__badge_code = badge_code


# noinspection PyClassHasNoInit
class VirtualSerial:
    Serial = _VirtualSerial
