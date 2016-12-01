import json
import errno
import socket
import logging
from socket import error as socket_error

from PackageInfo import PackageInfo
from ClientOptionParser import ClientOptionParser, ClientOption


class ClientSocket(object):
    def __init__(self, timeout=1.5):
        self.__logger = logging.getLogger(__name__)
        self.__opts = ClientOptionParser().parse_args()[0]
        self.__timeout = timeout

    def __enter__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.__timeout)
        self.socket.connect(('', self.__opts.get(ClientOption.CLIENT_PORT)))
        return self

    def send(self, opts, args):
        response = None
        try:
            self.socket.send(json.dumps({'opts': opts, 'args': args}))
            response = self.socket.recv(1024)
            self.socket.shutdown(socket.SHUT_RDWR)

        except socket_error as e:
            if e.errno != errno.ENOTCONN:
                raise e

        return response

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket.close()
        if exc_type:
            return False
