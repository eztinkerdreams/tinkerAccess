from mock import Mock


class Serial(Mock):
    pass


class MockSerial:
    Serial = Serial()
