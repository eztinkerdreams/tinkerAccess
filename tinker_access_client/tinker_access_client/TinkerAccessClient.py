import sys
import json
from Command import Command
from PackageInfo import PackageInfo
from ClientLogger import ClientLogger
from ClientDaemon import ClientDaemon
from ClientOptionParser import ClientOptionParser


# noinspection PyClassHasNoInit
class TinkerAccessClient(object):

    # TODO: this can be static
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
                if command is Command.START:
                    ClientDaemon.start()

                elif command is Command.STOP:
                    ClientDaemon.stop()

                elif command in [Command.RESTART, Command.RELOAD, Command.FORCE_RELOAD]:
                    ClientDaemon.restart()

                elif command is Command.STATUS:
                    ClientDaemon.status()

                else:
                    raise NotImplemented()

            except (KeyboardInterrupt, SystemExit):
                pass

            except Exception as e:
                logger.debug('%s \'%s\' command failed.', PackageInfo.pip_package_name, cmd)
                logger.exception(e)
                sys.exit(1)
