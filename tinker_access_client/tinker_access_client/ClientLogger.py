import os
import logging
import logging.handlers as handlers
from PackageInfo import PackageInfo
from ContextFilter import ContextFilter
from ClientOptionParser import ClientOptionParser, ClientOption


class ClientLogger(object):

    @staticmethod
    def setup(phase=None):
        logger = logging.getLogger(PackageInfo.python_package_name)
        (opts, args) = ClientOptionParser(phase=phase).parse_args()

        logger.filters = []
        logger.handlers = []

        debug_mode = opts.get(ClientOption.DEBUG)
        log_level = opts.get(ClientOption.LOG_LEVEL)
        if debug_mode:
            logger.setLevel(10)
        else:
            logger.setLevel(log_level if log_level else 40)

        logger.addFilter(ContextFilter(opts))

        sys_log_format = '%(asctime)s %(hostname)s %(app_id)s %(version)s %(device_id)s %(message)s'
        sys_log_formatter = logging.Formatter(sys_log_format, datefmt='%FT%T')

        # paperTrail
        log_address_for_paper_trail = opts.get(ClientOption.LOG_ADDRESS_FOR_PAPER_TRAIL)
        if log_address_for_paper_trail:
            (paper_trail_host, paper_trail_port) = log_address_for_paper_trail.split(':', 2)
            paper_trail_handler = handlers.SysLogHandler((paper_trail_host, int(paper_trail_port)))
            paper_trail_handler.setFormatter(sys_log_formatter)
            logger.addHandler(paper_trail_handler)

        # dev/log
        sys_log_file = '/var/log/syslog'
        if os.path.exists(sys_log_file):
            sys_log_handler = handlers.SysLogHandler('/dev/log')
            logger.addHandler(sys_log_handler)
            sys_log_handler.setFormatter(sys_log_formatter)

        # console
        logger.addHandler(logging.StreamHandler())

        # fileHandler
        log_file = opts.get(ClientOption.LOG_FILE)
        if log_file:
            if not os.path.exists(os.path.dirname(log_file)):
                os.makedirs(os.path.dirname(log_file))

            file_handler = handlers.TimedRotatingFileHandler(log_file, when='D', interval=1, backupCount=7)
            logger.addHandler(file_handler)

        return logger
