import json
import errno
import socket
import logging
import threading
from socket import error as socket_error

from Command import Command
from PackageInfo import PackageInfo
from CommandHandler import CommandHandler

# TODO: while technically functional, I plan to revisit this because there are a few things
# that can be improved i.e. use 'select' to wait for connections, self.__listener.accept blocks,
# which prevents the thread from exiting gracefully in the event of a non STOP command shutdown i.e. CTRL-C:


class RemoteCommandHandler(object):

    def __init__(self, execute_initial_command=False):
        self.__listener = None
        self.__logger = logging.getLogger(__name__)

        self.__handlers = []

    def __enter__(self):
        try:
            self.__listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

    def on(self, command, call_back):
        self.__handlers.append((command, call_back,))

    def __listen(self):
        cmd = None
        while cmd is not Command.STOP:
            client = None

            try:
                (client, addr) = self.__listener.accept()
                data = json.loads(client.recv(1024))
                opts = data.get('opts')
                args = data.get('args')
                cmd = Command(args[0]) if len(args) >= 1 else None
                response = self.wait(opts, args)

                if isinstance(response, basestring):
                    client.send(response or '')
                client.shutdown(socket.SHUT_RDWR)

            except socket_error as e:
                # TODO: ignored for now, need to work out some issues to exit gracefully
                # will probably replace .accept with .select
                pass
                # if e.errno != errno.ENOTCONN:
                #     self.__logger.exception(e)
                #     raise e

            except Exception as e:
                self.__logger.exception(e)
                raise e

            finally:
                if client:
                    client.close()

    def listen(self):
        t = threading.Thread(name='remote-command-handler', target=self.__listen)
        t.daemon = True
        t.start()

    # TODO: will be removing this in favor of select
    def wait(self, opts, args):
        cmd = Command(args[0].lower() if len(args) >= 1 and len(args[0].lower()) >= 1 else None)

        result = None
        if cmd and len(self.__handlers):
            for (command, call_back) in self.__handlers:
                if command is cmd:
                    try:
                        result = call_back(opts=opts, args=args)
                    except Exception as e:
                        self.__logger.exception(e)

        return result

