from BaseHTTPServer import HTTPServer
from VirtualDeviceHandler import VirtualDeviceHandler
from tinker_access_client.ClientLogger import ClientLogger
from tinker_access_client.ClientOptionParser import ClientOptionParser, ClientOption


# noinspection PyClassHasNoInit
class VirtualDeviceServer:

    @staticmethod
    def start():
        logger = ClientLogger.setup()
        debug_port = ClientOptionParser().parse_args()[0].get(ClientOption.DEBUG_PORT)
        try:
            server = HTTPServer(('', debug_port), VirtualDeviceHandler)
            msg = '\033[92m' \
                  '********************************************************************************\n' \
                  'Virtual Device Initialized, Go To: http://localhost:{0}                         \n' \
                  '********************************************************************************' \
                  '\033[0m'.format(debug_port)
            logger.info(msg)
            server.serve_forever()

        except KeyboardInterrupt:
            server.socket.close()




