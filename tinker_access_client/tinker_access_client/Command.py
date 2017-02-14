from PackageInfo import PackageInfo

chars = 8


class Command(object):

    START = dict(
        command='start'.ljust(chars),
        description='This command will start the {0}.\n'.format(PackageInfo.pip_package_name)
    )
    STOP = dict(
        command='stop'.ljust(chars),
        description='This command will stop the {0}.\n'.format(PackageInfo.pip_package_name)
    )
    STATUS = dict(
        command='status'.ljust(chars),
        description='This command will return the current state of the {0}\n'
                    '\t\t   (i.e. initialized, idle, in_use, in_training, terminated)\n'
                    .format(PackageInfo.pip_package_name)
    )
    RESTART = dict(
        command='restart'.ljust(chars),
        description='This command will stop the {0}.\n'.format(PackageInfo.pip_package_name)
    )
    UPDATE = dict(
        command='update'.ljust(chars),
        description='This command will update the {0} using PyPI - the Python Package Index,\n'
        '\t\t   by default the latest published version will be installed.\n'
        '\t\t   Optionally a second argument can be provided to specify the specific version desired. \n'
        '\t\t   (i.e. \'sudo {0} update 2017.2.14.441\')\n'.format(PackageInfo.pip_package_name)
    )

    # RELOAD = dict(command='reload', description='reload...')
    # REMOVE = dict(command='remove', description='remove...')
    # UNINSTALL = dict(command='uninstall', description='uninstall...')
    # RECONFIGURE = dict(command='re-configure', description='re-configure...')
    # FORCE_RELOAD = dict(command='force_reload', description='force_reload...')

    def __new__(self, command):
        for key, value in vars(Command).items():
            if not key.startswith('__'):
                if command == value['command']:
                    return value

        return None
