import socket
import logging
from PackageInfo import PackageInfo
from ClientOptionParser import ClientOption


class ContextFilter(logging.Filter):
    def __init__(self, opts):
        self.__hostname = socket.gethostname()
        self.__device_id = opts.get(ClientOption.DEVICE_ID)
        self.__app_id = PackageInfo.pip_package_name
        self.__version = PackageInfo.version

    def filter(self, record):
        record.hostname = self.__hostname
        record.app_id = self.__app_id
        record.device_id = self.__device_id
        record.version = self.__version

        # TODO: be nice to have action, user_id, badge_id etc..
        record.user_id = None
        record.badge_id = None
        record.user_name = None
        record.action = None

        return True
