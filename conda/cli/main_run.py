# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from logging import getLogger
import os
from subprocess import PIPE, Popen
import sys

from ..base.context import context
from ..utils import wrap_subprocess_call
from ..gateways.disk.delete import rm_rf


def execute(args, parser):
    on_win = sys.platform == "win32"

    # import time
    # while not 'CONTINUAR' in os.environ:
    #     print("Please set CONTINUAR env var", file=sys.stderr)
    #     time.sleep(0.5)

    # import pdb; pdb.set_trace()

    call = args.executable_call
    prefix = args.prefix or os.getenv("CONDA_PREFIX") or context.root_prefix
    env = os.environ.copy()

    script_caller, command_args = wrap_subprocess_call(on_win, context.root_prefix, prefix,
                                                       args.dev, args.debug_wrapper_scripts, call)
    env = os.environ.copy()
    from conda.gateways.subprocess import _subprocess_clean_env
    _subprocess_clean_env(env, clean_python=True, clean_conda=True)
    process = Popen(command_args, universal_newlines=False, stdout=PIPE, stderr=PIPE, env=env)
    stdout, stderr = process.communicate()
    if hasattr(stdout, "decode"): stdout = stdout.decode('utf-8', errors='replace')
    if hasattr(stderr, "decode"): stderr = stderr.decode('utf-8', errors='replace')
    if stdout:
        sys.stdout.write(stdout)
    if stderr:
        sys.stderr.write(stderr)
    if process.returncode != 0:
        log = getLogger(__name__)
        log.error("Subprocess for 'conda run {}' command failed.  Stderr was:\n{}"
                  .format(call, stderr))
    if script_caller is not None:
        if not 'CONDA_TEST_SAVE_TEMPS' in os.environ:
            rm_rf(script_caller)
        else:
            log = getLogger(__name__)
            log.warning('CONDA_TEST_SAVE_TEMPS :: retaining main_run script_caller {}'.format(script_caller))
