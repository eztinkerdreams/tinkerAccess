class Command(object):
    START = dict(command='start', description='start desc...')
    STOP = dict(command='stop', description='stop desc...')
    STATUS = dict(command='status', description='status desc...')
    UPDATE = dict(command='update', description='update...')
    RESTART = dict(command='restart', description='restart...')
    RELOAD = dict(command='reload', description='reload...')
    # REMOVE = dict(command='remove', description='remove...')
    # UNINSTALL = dict(command='uninstall', description='uninstall...')
    # RECONFIGURE = dict(command='re-configure', description='re-configure...')
    FORCE_RELOAD = dict(command='force_reload', description='force_reload...')

    def __new__(self, command):
        for key, value in vars(Command).items():
            if not key.startswith('__'):
                if command == value['command']:
                    return value

        return None
