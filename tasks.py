from invoke import Task, Context
from typing import Any


@Task
def deploy(c, env=None, force=False):  # type: (Context, str, bool) -> Any
    if env is None:
        print('--env=[dev|prd|...]')
        return

    options = [
        '--region ap-northeast-1'
    ]
    if force:
        options.append('--recreate-failed')

    c.run(f'stacker build {" ".join(options)} conf/{env}.env stacker.yaml')


@Task
def plan(c, env=None):  # type: (Context, str) -> Any
    if env is None:
        print('--env=[dev|prd|...]')
        return

    options = [
        '--region ap-northeast-1',
        '-o'
    ]

    c.run(f'stacker build {" ".join(options)} conf/{env}.env stacker.yaml')


@Task
def info(c, env=None):  # type: (Context, str) -> Any
    if env is None:
        print('--env=[dev|prd|...]')
        return

    c.run(f'stacker info conf/{env}.env stacker.yaml')


@Task
def diff(c, env=None):  # type: (Context, str) -> Any
    if env is None:
        print('--env=[dev|prd|...]')
        return

    c.run(f'stacker diff conf/{env}.env stacker.yaml')
