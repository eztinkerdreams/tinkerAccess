
from CommandHandler import CommandHandler


class RemoteCommandHandler(CommandHandler):
    if __name__ == '__main__':
        def __init__(self):
            super(CommandHandler, self).__init__(False)
            #TODO: init remote listening socket.
            #: move code from client run_listener

    #This will be moved to some other class I am sure...
    def run_listener(self):

        pass

        # self.__logger.debug('Attempting to establish %s listener...', PackageInfo.pip_package_name)
        #
        # server = None
        #
        # try:
        #     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #
        #     #TODO: this line causes some major proble, no exception is thrown
        #     #listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #
        #     server.bind(('', 8089))
        #     server.settimeout(None)
        #     server.listen(5)
        #
        #     now = time.time()
        #     while not self.__should_exit:
        #         self.__logger.debug('listener started...')
        #         client = None
        #
        #         try:
        #             (client, addr) = server.accept()
        #             command = Command(client.recv(1024))
        #             if command:
        #                 self.__logger.debug('%s listener received \'%s\' command',
        #                                     PackageInfo.pip_package_name, command)
        #
        #                 #TODO: allow for graceful shutdown..
        #                 if command is Command.STOP:
        #                     self.__stop()
        #                     break
        #                 else:
        #                     # send a standard response, possibly JSON...
        #                     client.send('State: {0}'.format(self.state))
        #
        #             client.shutdown(socket.SHUT_RDWR)
        #
        #         except socket_error as e:
        #             if e.errno != errno.ENOTCONN:
        #                 self.__logger.exception(e)
        #                 raise e
        #
        #         except Exception as e:
        #             self.__logger.exception(e)
        #             raise e
        #
        #         finally:
        #             if client:
        #                 client.close()
        #
        #         if not self.__should_exit:
        #             self.__logger.debug('will stop listening...')
        #
        # except Exception as e:
        #     self.__logger.debug('Unable to establish the %s listener.', PackageInfo.pip_package_name)
        #     self.__logger.exception(e)
        #     thread.interrupt_main()
        #
        # finally:
        #     if server:
        #         server.shutdown(socket.SHUT_RDWR)
        #         server.close()
