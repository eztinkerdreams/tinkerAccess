class _VirtualSerial(object):
    def __init__(self, *args):
        pass

    # noinspection PyPep8Naming
    def flushInput(self, *args):
        pass

    # noinspection PyPep8Naming
    def flushOutput(self, *args):
        pass


# noinspection PyClassHasNoInit
class VirtualSerial:
    Serial = _VirtualSerial
