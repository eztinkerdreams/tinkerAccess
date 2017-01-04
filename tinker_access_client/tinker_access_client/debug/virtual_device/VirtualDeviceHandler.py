# from tinker_access_client.tinker_access_client.ClientLogger import ClientLogger
# from tinker_access_client.ClientOptionParser import ClientOptionParser, ClientOption
from BaseHTTPServer import BaseHTTPRequestHandler

initial_pin_state = [
    [
        {'pin': 2, 'desc': '5v Power', 'status': False},
        {'pin': 4, 'desc': '5v Power', 'status': False},
        {'pin': 6, 'desc': 'Ground', 'status': False},
        {'pin': 8, 'desc': 'BCM 14', 'status': True},
        {'pin': 10, 'desc': 'BCM 15', 'status': True},
        {'pin': 12, 'desc': 'BCM 18', 'status': True},
        {'pin': 14, 'desc': 'Ground', 'status': False},
        {'pin': 16, 'desc': 'BCM 23', 'status': True},
        {'pin': 18, 'desc': 'BCM 24', 'status': True},
        {'pin': 20, 'desc': 'Ground', 'status': False},
        {'pin': 22, 'desc': 'BCM 25', 'status': True},
        {'pin': 24, 'desc': 'BCM 8', 'status': True},
        {'pin': 26, 'desc': 'BCM 7', 'status': True},
        {'pin': 28, 'desc': 'BCM 1', 'status': True},
        {'pin': 30, 'desc': 'Ground', 'status': False},
        {'pin': 32, 'desc': 'BCM 12', 'status': True},
        {'pin': 34, 'desc': 'Ground', 'status': False},
        {'pin': 36, 'desc': 'BCM 16', 'status': True},
        {'pin': 38, 'desc': 'BCM 20', 'status': True},
        {'pin': 40, 'desc': 'BCM 21', 'status': True}],
    [
        {'pin': 1, 'desc': '3v3 Power', 'status': False},
        {'pin': 3, 'desc': 'BCM 2', 'status': False},
        {'pin': 5, 'desc': 'BCM 3', 'status': False},
        {'pin': 7, 'desc': 'BCM 4', 'status': False},
        {'pin': 9, 'desc': 'Ground', 'status': False},
        {'pin': 11, 'desc': 'BCM 17', 'status': True},
        {'pin': 13, 'desc': 'BCM 27', 'status': True},
        {'pin': 15, 'desc': 'BCM 22', 'status': True},
        {'pin': 17, 'desc': '3v3 Power', 'status': False},
        {'pin': 19, 'desc': 'BCM 10', 'status': True},
        {'pin': 21, 'desc': 'BCM 9', 'status': True},
        {'pin': 23, 'desc': 'BCM 11', 'status': True},
        {'pin': 25, 'desc': 'Ground', 'status': False},
        {'pin': 27, 'desc': 'BCM 0', 'status': True},
        {'pin': 29, 'desc': 'BCM 5', 'status': True},
        {'pin': 31, 'desc': 'BCM 6', 'status': True},
        {'pin': 33, 'desc': 'BCM 13', 'status': True},
        {'pin': 35, 'desc': 'BCM 19', 'status': True},
        {'pin': 37, 'desc': 'BCM 26', 'status': True},
        {'pin': 39, 'desc': 'Ground', 'status': False}
    ]
]


class VirtualDeviceHandler(BaseHTTPRequestHandler):

    # def __init__(self):
    #     self.__pins = initial_pin_state[:]
    #     # self.__logger = ClientLogger.setup()
    #     # self.__logger.debug('New Handler created....')
    #     # self.__debug_port = ClientOptionParser().parse_args()[0].get(ClientOption.DEBUG_PORT)

    def do_GET(self):
        self.send_response(200)
        #raise NotImplemented

    def do_POST(self):
        self.send_response(200)
        #raise NotImplemented
