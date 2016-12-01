import os
import logging
import logging.handlers as handlers
from ContextFilter import ContextFilter
from ClientOptionParser import ClientOptionParser, ClientOption


class ClientLogger(object):

    @staticmethod
    def setup(phase=None):
        (opts, args) = ClientOptionParser(phase=phase).parse_args()
        logger = logging.getLogger()

        logger.filters = []
        logger.handlers = []
        logger.setLevel(opts.get(ClientOption.LOG_LEVEL) if not opts.get(ClientOption.DEBUG) else logging.DEBUG)

        # dev/log
        sys_log_file = '/var/log/syslog'
        if os.path.exists(sys_log_file):
            sys_log_handler = handlers.SysLogHandler('/dev/log')
            sys_log_format = \
                '%(app_id)s %(version)s %(device_id)s %(device_name)s ' \
                '%(user_id)s %(user_name)s %(badge_code)s %(message)s'
            sys_log_formatter = logging.Formatter(sys_log_format)
            sys_log_handler.setFormatter(sys_log_formatter)
            sys_log_handler.addFilter(ContextFilter(opts))
            logger.addHandler(sys_log_handler)

        # console
        logger.addHandler(logging.StreamHandler())

        # fileHandler
        try:
            log_file = opts.get(ClientOption.LOG_FILE)
            if log_file:
                if not os.path.exists(os.path.dirname(log_file)):
                    os.makedirs(os.path.dirname(log_file))

                file_handler = handlers.TimedRotatingFileHandler(
                    log_file, when='D', interval=1, backupCount=7)
                logger.addHandler(file_handler)
        except Exception as e:
            logger.exception(e)

        return logger
