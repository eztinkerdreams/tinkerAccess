#!/usr/bin/env python

### BEGIN INIT INFO
# Provides:          tinker-access-client
# Required-Start:    $remote_fs $syslog $network
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: tinker-access-client
# Description:       The tinker-access-client service is responsible for coordinating communication
# between RPi's modules (i.e. RFID reader, LCD, power relays etc..) and the remote tinker_access_server.
### END INIT INFO

import sys
import logging
from PackageInfo import PackageInfo
from ClientLogger import ClientLogger
from ClientDaemon import ClientDaemon
from CommandHandler import CommandHandler
from ClientOptionParser import ClientOptionParser, Command


def run():
    logger = ClientLogger.setup()
    try:
        with CommandHandler() as handler:
            handler.on(Command.STOP, ClientDaemon.stop)
            handler.on(Command.START, ClientDaemon.start)
            handler.on(Command.UPDATE, ClientDaemon.update)
            handler.on(Command.STATUS, ClientDaemon.status)
            handler.on(Command.RESTART, ClientDaemon.restart)

            # TODO: UNINSTALL, RE-CONFIGURE, GET-CONFI-VALUE, SET-CONFIG-VALUE, GET-CONFIGS

            (opts, args) = ClientOptionParser().parse_args()
            handler.wait(opts, args)

    except (KeyboardInterrupt, SystemExit):
        pass

    except Exception as e:
        logger.debug('%s failed to handle the command.', PackageInfo.pip_package_name)
        logger.exception(e)
        sys.stdout.write(str(e))
        sys.stdout.flush()
        sys.exit(1)

    finally:
        logging.shutdown()

if __name__ == '__main__':
    run()
