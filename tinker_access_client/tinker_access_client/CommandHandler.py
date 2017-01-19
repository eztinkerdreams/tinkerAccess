import sys
import time
import json
from Command import Command
from PackageInfo import PackageInfo
from ClientLogger import ClientLogger
# from ClientDaemon import ClientDaemon
from ClientOptionParser import ClientOptionParser


# noinspection PyClassHasNoInit
class CommandHandler(object):

    def __init__(self, execute_initial_command=True):
        self.__logger = ClientLogger.setup()
        (opts, args) = ClientOptionParser().parse_args()
        cmd = Command(args[0].lower() if len(args) >= 1 and len(args[0].lower()) >= 1 else None)
        self.__handlers = [] #TODO: convert to queue or requeue

    # TODO: add test and implement... __enter__, __exit__
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    # def __del__(self):
    #     pass

    def wait(self, opts, args):
        cmd = Command(args[0].lower() if len(args) >= 1 and len(args[0].lower()) >= 1 else None)

        result = None
        # while not cmd or (self.__command and not len(self.__handlers)):
        #     time.sleep(0.250)

        if cmd and len(self.__handlers):
            for (command, call_back) in self.__handlers:
                if command is cmd:
                    try:
                        result = call_back(opts=opts, args=args)
                    except Exception as e:
                        self.__logger.exception(e)

        return result

    def on_command(self, call_back):
        # TODO: implement... probably will need another thread..
        pass

    def on(self, command, call_back):
        self.__handlers.append((command, call_back,))