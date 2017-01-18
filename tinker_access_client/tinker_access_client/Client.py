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
from CommandHandler import CommandHandler
from ClientOptionParser import ClientOptionParser, ClientOption


class State(object):
    INITIALIZED = 'INITIALIZED'
    IDLE = 'IDLE'


class Client(Machine):
    def __init__(self):
        self.__logger = ClientLogger.setup()
        self.__opts = ClientOptionParser().parse_args()[0]
        self.__should_exit = False

        states = []
        for key, _ in vars(State).items():
            if not key.startswith('__'):
                states.append(key)

        Machine.__init__(self, states=states, initial=State.INITIALIZED)

    #This will be moved to some other class I am sure...
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
            while not self.__should_exit:
                self.__logger.debug('listener started...')
                client = None

                try:
                    (client, addr) = server.accept()
                    command = Command(client.recv(1024))
                    if command:
                        self.__logger.debug('%s listener received \'%s\' command',
                                            PackageInfo.pip_package_name, command)

                        #TODO: allow for graceful shutdown..
                        if command is Command.STOP:
                            self.__stop()
                            break
                        else:
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

                if not self.__should_exit:
                    self.__logger.debug('will stop listening...')

        except Exception as e:
            self.__logger.debug('Unable to establish the %s listener.', PackageInfo.pip_package_name)
            self.__logger.exception(e)
            thread.interrupt_main()

        finally:
            if server:
                server.shutdown(socket.SHUT_RDWR)
                server.close()

    def __handle_status_command(self):
        pass

    def __handle_stop_command(self):
        self.__stop()

    def __stop(self):
        self.__should_exit = True
        #TODO: wait for client status(self.state) to be done before we exit...

    def __run(self):
        with CommandHandler() as handler:
            handler.on(Command.STOP, self.__handle_stop_command)
            handler.on(Command.STATUS, self.__handle_status_command)
            with DeviceApi(self.__opts) as device:
                #device.on('channdle', 'handler')
                #etc....

                while not self.__should_exit:

                    #TODO: remove this message when the complete implementation is final...
                    self.__logger.debug('%s is running...', PackageInfo.pip_package_name)

                    device.wait_for_edge()

    def run(self):
        while not self.__should_exit:
            try:
                self.__run()
            except Exception as e:
                self.__logger.exception(e)


