import time

import socket
from threading import Thread

from transitions import Machine
# TODO: Enable LockedHierarchicalGraphMachine https://github.com/tyarkoni/transitions#-extensions
# from transitions.extensions import LockedHierarchicalGraphMachine as Machine

from PackageInfo import PackageInfo
from ClientLogger import ClientLogger
from DeviceApi import DeviceApi, Channel
from ClientOptionParser import ClientOptionParser


class State(object):
    INITIALIZED = 'INITIALIZED'
    IDLE = 'IDLE'


class Client(Machine):
    def __init__(self):
        self.__logger = ClientLogger.setup()
        self.__opts = ClientOptionParser().parse_args()[0]
        self.__deviceApi = DeviceApi(self.__opts)

        states = []
        for key, _ in vars(State).items():
            if not key.startswith('__'):
                states.append(key)

        Machine.__init__(self, states=states, initial=State.INITIALIZED)

    def listen_2(self):
        print 'listen....'
        try:
            while True:
                self.__logger.debug('Listening: %s....', self.server_socket.getsockname())
                (conn, addr) = self.server_socket.accept()
                self.__logger.debug('message: {0}, {1}'.format(conn, addr))
        except (KeyboardInterrupt, SystemExit):
            self.__logger.debug('exit..')
            self.server_socket.close()
        except Exception as e:
            self.__logger.exception(e)

    def listen(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('127.0.0.1', 8089))
        server_socket.listen(5)
        self.server_socket = server_socket

        t = Thread(target=self.listen_2)
        t.daemon = True
        t.start()

        # # TODO: review... I'm in the 'get it working phase now'
        # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # server_socket.bind(('localhost', 8089))
        # server_socket.listen(5)
        # self.server_socket = server_socket

    def run(self):
        try:
            self.listen()

            wait = 5
            counter = 0
            while counter < 720:
                counter += 1
                time.sleep(wait)
                self.__logger.debug('%s running for %s seconds...', PackageInfo.pip_package_name, counter * wait)

        except KeyboardInterrupt as e:
            self.__logger.debug('Keyboard-Interrupt')
            raise e

        except SystemExit as e:
            self.__logger.debug('System-Exit, process killed')
            raise e

        except Exception as e:
            self.__logger.debug('Unable to start the %s daemon.')
            self.__logger.exception(e)
            raise e
