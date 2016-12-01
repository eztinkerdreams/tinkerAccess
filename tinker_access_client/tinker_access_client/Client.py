import time

from PackageInfo import PackageInfo
from ClientLogger import ClientLogger
from DeviceApi import DeviceApi, Channel
from ClientOptionParser import ClientOptionParser


class Client(object):

    def __init__(self):
        self.__logger = ClientLogger.setup()
        self.__opts = ClientOptionParser().parse_args()[0]
        self.__deviceApi = DeviceApi(self.__opts)

    def run(self):
        try:
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
