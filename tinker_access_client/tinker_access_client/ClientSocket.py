import errno
import socket
from socket import error as socket_error

from Command import Command
from PackageInfo import PackageInfo
from ClientLogger import ClientLogger
from ClientOptionParser import ClientOptionParser, ClientOption


class ClientSocket(object):
    def __init__(self, timeout=1.5):
        self.__logger = ClientLogger.setup()
        self.__opts = ClientOptionParser().parse_args()[0]
        self.__timeout = timeout

    def __enter__(self):
        self.__logger.debug('Attempting to create %s socket...', PackageInfo.pip_package_name)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.__timeout)
        self.__logger.debug('Attempting to connect %s socket...', PackageInfo.pip_package_name)
        self.socket.connect(('', self.__opts.get(ClientOption.CLIENT_PORT)))
        return self

    def send(self, cmd):
        response = None
        try:
            command = cmd.get('command')
            self.__logger.debug(
                'Attempting to send \'%s\' command to %s socket...',
                command,
                PackageInfo.pip_package_name)
            self.socket.send(command)

            self.__logger.debug('Attempting to receive from %s socket...', PackageInfo.pip_package_name)
            response = self.socket.recv(1024)

            self.__logger.debug('Attempting to shutdown %s socket...', PackageInfo.pip_package_name)
            self.socket.shutdown(socket.SHUT_RDWR)

        except socket_error as e:
            if e.errno != errno.ENOTCONN:
                raise e

        return response

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__logger.debug('Attempting to close %s socket...', PackageInfo.pip_package_name)
        self.socket.close()

        if exc_type:
            return False

