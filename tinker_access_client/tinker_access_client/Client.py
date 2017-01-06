import sys
import time

import errno
import socket
from socket import error as socket_error

# from threading import Thread
import thread

from transitions import Machine
# TODO: Enable LockedHierarchicalGraphMachine https://github.com/tyarkoni/transitions#-extensions
# from transitions.extensions import LockedHierarchicalGraphMachine as Machine

from Command import Command
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

    # def listen(self):
    #     while True:
    #         conn = None
    #         try:
    #             (conn, addr) = self.__listener.accept()
    #             command = Command(conn.recv(1024))
    #             if command:
    #                 self.__logger.debug('Command received...%s', command)
    #
    #                 #send the response...
    #                 conn.send('State: {0}'.format(self.state))
    #         except (KeyboardInterrupt, SystemExit):
    #                 self.__logger.debug('exit..')
    #                 self.__listener.close()
    #         except Exception as e:
    #             self.__logger.exception(e)
    #             raise e
    #         finally:
    #             conn.close()

    def run_listener(self):
        self.__logger.debug('Attempting to establish %s listener...', PackageInfo.pip_package_name)

        server = None

        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            #TODO: this line causes some major proble, no exception is thrown
            #listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            server.bind(('', 8089))
            server.settimeout(None)
            server.listen(5)

            now = time.time()
            while True:
                client = None

                try:
                    self.__logger.debug('%s listener running for %s seconds...',
                                        PackageInfo.pip_package_name,
                                        int(now - time.time()))

                    (client, addr) = server.accept()
                    command = Command(client.recv(1024))
                    if command:
                        self.__logger.debug('%s listener received \'%s\' command',
                                            PackageInfo.pip_package_name, command)

                        # send a standard response, possibly JSON...
                        client.send('State: {0}'.format(self.state))

                    client.shutdown(socket.SHUT_RDWR)

                except socket_error as e:
                    if e.errno != errno.ENOTCONN:
                        self.__logger.exception(e)
                        raise e

                except Exception as e:
                    self.__logger.exception(e)
                    raise e

                finally:
                    if client:
                        client.close()

        except Exception as e:
            self.__logger.debug('Unable to establish the %s listener.', PackageInfo.pip_package_name)
            self.__logger.exception(e)
            thread.interrupt_main()

        finally:
            if server:
                server.shutdown(socket.SHUT_RDWR)
                server.close()

    def run_client(self):
        try:
            wait = 5
            counter = 0
            while counter < 720:
                counter += 1
                time.sleep(wait)
                self.__logger.debug('%s daemon running for %s seconds...', PackageInfo.pip_package_name, counter * wait)

        except (SystemExit, KeyboardInterrupt) as e:
            self.__logger.debug('%s daemon stopping...', PackageInfo.pip_package_name)
            raise e

        except Exception as e:
            self.__logger.debug('Unable to start the %s daemon.', PackageInfo.pip_package_name)
            self.__logger.exception(e)
            raise e

    def run(self):
        try:
            thread.start_new_thread(self.run_listener, ())
            self.run_client()
        except Exception as e:
            self.__logger.exception(e)
            raise e
