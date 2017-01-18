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
from PackageInfo import PackageInfo
from ClientLogger import ClientLogger
from ClientDaemon import ClientDaemon
from CommandHandler import CommandHandler
from ClientOptionParser import ClientOptionParser, Command


def run():
    logger = ClientLogger.setup()
    cmd = ClientOptionParser().parse_args()[1][0]
    logger.debug('Attempting to handle %s \'%s\' command...', PackageInfo.pip_package_name, cmd)
    try:
        with CommandHandler() as handler:
            handler.on(Command.STOP, ClientDaemon.stop)
            handler.on(Command.START, ClientDaemon.start)
            handler.on(Command.STATUS, ClientDaemon.status)
            #handler.on(Command.UPDATE, ClientDaemon.up)
            #handler.on(Command.RESTART, ClientDaemon.restart)
            #handler.on(Command.RELOAD, ClientDaemon.start)
            #handler.on(Command.REMOVE, ClientDaemon.start)
            #handler.on(Command.UNINSTALL, ClientDaemon.start)
            #handler.on(Command.RECONFIGURE, ClientDaemon.start)
            #handler.on(Command.FORCE_RELOAD, ClientDaemon.start)
            handler.wait()

    except (KeyboardInterrupt, SystemExit):
        pass

    except Exception as e:
        logger.debug('%s failed to handle \'%s\' command.', PackageInfo.pip_package_name, cmd)
        logger.exception(e)
        sys.stdout.write(str(e))
        sys.stdout.flush()
        sys.exit(1)

if __name__ == '__main__':
    run()
