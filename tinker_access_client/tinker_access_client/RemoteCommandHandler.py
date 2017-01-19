import time
import json
import errno
import socket
from socket import error as socket_error

import threading

import thread
from Command import Command
from PackageInfo import PackageInfo
from ClientLogger import ClientLogger
from CommandHandler import CommandHandler


class RemoteCommandHandler(CommandHandler):

    def __init__(self, execute_initial_command=False):
        self.__client = None
        self.__listener = None
        self.__should_exit = None
        self.__logger = ClientLogger.setup()
        super(RemoteCommandHandler, self).__init__(execute_initial_command)

    def __enter__(self):
        try:
            self.__listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            #TODO: this line causes some major proble, no exception is thrown
            self.__listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.__listener.bind(('', 8089)) # TODO: add and use additional config value for this listener
            self.__listener.settimeout(None)
            self.__listener.listen(5)

            # TODO: lookup async select patterns with sockets in python, or other libraries to use
            # to reduce this boiler plate code
        except Exception as e:
            self.__logger.debug('Unable to establish the %s listener.', PackageInfo.pip_package_name)
            self.__logger.exception(e)
            #thread.interrupt_main()  # TODO: investigate further, causing the unit test to fail and builds to fail

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: reuse for client...
        if self.__listener:
            try:
                self.__listener.shutdown(socket.SHUT_RDWR)
            except socket_error as e:
                if e.errno != errno.ENOTCONN:
                    self.__logger.exception(e)
                    raise e

            except Exception as e:
                self.__logger.exception(e)
                raise e
            finally:
                self.__listener.close()

    def __listen(self):

        while True:
            client = None

            try:
                self.__logger.debug('%s listener is waiting for command...', PackageInfo.pip_package_name)
                (client, addr) = self.__listener.accept()
                data = json.loads(client.recv(1024))
                opts = data.get('opts')
                args = data.get('args')
                response = self.wait(opts, args)
                client.send(response or '')
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

    def listen(self):
        t = threading.Thread(name='listener', target=self.__listen)
        t.daemon = True
        t.start()

