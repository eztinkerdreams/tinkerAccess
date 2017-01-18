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
    def __init__(self):
        self.__logger = ClientLogger.setup()
        (opts, args) = ClientOptionParser().parse_args()
        cmd = Command(args[0].lower() if len(args) >= 1 and len(args[0].lower()) >= 1 else None)
        self.__command = (cmd, opts, args) if cmd else None
        self.__handlers = []

    # TODO: add test and implement... __enter__, __exit__
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    # def __del__(self):
    #     pass

    def wait(self):
        while not self.__command:
            time.sleep(0.250)

        if self.__handlers:
            for (command, call_back) in self.__handlers:
                (cmd, opts, args) = self.__command
                if command is cmd:
                    call_back(opts=opts, args=args)
            self.__command = None

    def on_command(self, call_back):
        # TODO: implement... probably will need another thread..
        pass

    def on(self, command, call_back):
        self.__handlers.append((command, call_back,))

    # noinspection PyMethodMayBeStatic
    def run(self):
        logger = ClientLogger.setup()
        (opts, args) = ClientOptionParser().parse_args()
        cmd = args[0].lower() if len(args) >= 1 and len(args[0].lower()) >= 1 else None
        command = Command(cmd)

        if command is not None:

            logger.debug(
                'Attempting to handle %s \'%s\' command with:\n%s',
                PackageInfo.pip_package_name, cmd,
                json.dumps(opts, indent=4, sort_keys=True)
            )

            try:
                # #TODO: these should be moved into a command_handler routine inside the ClientDeamom class
                # #since the command handler can be generic now using the on_command call back
                #
                # if command is Command.START:
                #     ClientDaemon.start()
                #
                # elif command is Command.STOP:
                #     ClientDaemon.stop()
                #
                # elif command in [Command.RESTART, Command.RELOAD, Command.FORCE_RELOAD]:
                #     ClientDaemon.restart()
                #
                # elif command is Command.STATUS:
                #     ClientDaemon.status()
                #
                # else:
                #     raise NotImplemented()

                self.__handle_command(command)

            except (KeyboardInterrupt, SystemExit):
                #  TODO: might not be needed here?
                pass

            except Exception as e:
                logger.debug('%s \'%s\' command failed.', PackageInfo.pip_package_name, cmd)
                logger.exception(e)
                sys.exit(1)



        else:
            raise NotImplemented

            # except (KeyboardInterrupt, SystemExit):
            #     #  TODO: might not be needed here?
            # pass
