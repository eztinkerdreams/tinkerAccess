import os
import logging
import tempfile
import subprocess


# noinspection PyClassHasNoInit
class CommandExecutor:

    @staticmethod
    def ensure_execute_permission(path):
        os.chmod(path, 0755)

    @staticmethod
    def execute_commands(commands):
        # I suppose an explanation is warranted here...
        # Unfortunately we cannot execute these commands directly from python due to the fact that the
        # start priority 91 must be passed to the update-rc command as an integer and python converts all arguments to
        # strings which causes and exception when the update command is invoked.
        # We work around the problem by creating a temporary script file and executing that
        fd, path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, 'w') as tmp:
                tmp.writelines(['#!/usr/bin/env bash\n'] + commands)
            CommandExecutor.ensure_execute_permission(path)
            CommandExecutor.execute_command(path)
        finally:
            os.remove(path)

    @staticmethod
    def execute_command(command):
        logger = logging.getLogger(__name__)
        try:
            cmd = [command] + ['-evx']  # Options: http://www.tldp.org/LDP/abs/html/options.html
            cmd_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_data, stderr_data = cmd_process.communicate()
            if cmd_process.returncode != 0:
                for ln in stderr_data.splitlines(True):
                    logger.error(ln)
                raise RuntimeError('{0} command failed.\n'.format(cmd))
            else:
                for ln in stdout_data.splitlines(True):
                    logger.debug(ln)
        except RuntimeError as e:
            raise e
        except Exception as e:
            logger.exception(e)
            raise e
