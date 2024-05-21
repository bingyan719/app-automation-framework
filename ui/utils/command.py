import sys
import subprocess
from six import PY3

from ui.utils.snippet import get_std_encoding, split_cmd
from ui.utils.log import Logging


def execute(cmds):
    """
    Start a subprocess with command(s)
    Args:
        cmds: command(s) to be run
    Returns:
        a subprocess
    """
    cmds = split_cmd(cmds)
    cmd = 'execute command: {}'.format(" ".join(cmds))
    Logging.debug(cmd)

    if not PY3:
        cmds = [c.encode(get_std_encoding(sys.stdin)) for c in cmds]

    proc = subprocess.Popen(
        cmds,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return proc


def cmd(cmds, ensure_unicode=True, ignore_error=False, print_error=True):
    proc = execute(cmds)
    stdout, stderr = proc.communicate()
    if ensure_unicode:
        stdout = stdout.decode(get_std_encoding(sys.stdout))
        stderr = stderr.decode(get_std_encoding(sys.stderr))
    if stderr and print_error:
        Logging.error('execute command has an exception...')
        for line in stderr.splitlines():
            Logging.error(line)
    if not ignore_error and proc.returncode > 0:
        raise RuntimeError('command run with exception.')
    return stdout


