import os
import sys
from collections import namedtuple
from inspect import signature

import click


def format_message(message, arg):
    return message


def plain(msg, api=None, newline=True):
    click.secho(format_message(msg, api), nl=newline, fg='white')


def info(msg, api=None, newline=True):
    click.secho(format_message(msg, api), nl=newline, fg='green')


def warn(msg, api=None, newline=True):
    click.secho(format_message(msg, api), nl=newline, fg='yellow')


def fail(msg, api=None, newline=True):
    click.secho(format_message(msg, api), nl=newline, fg='red')


def note(msg, api=None, newline=True):
    click.secho(format_message(msg, api), nl=newline, fg='cyan')


Step = namedtuple('Step', ('name', 'func', 'exit_codes'))


class StepHandlerRegistry(object):

    def __init__(self):
        # Here we see why we use python 3: dicts are ordered!
        self.registry = []

    @property
    def registry_title(self):
        raise NotImplementedError

    def register(self, name, func, exit_codes=(0, )):
        """Registers a step."""
        assert name not in self.registry, "Can't register name twice"
        assert 'dry_run' in signature(func).parameters, \
            'Implement a dry_run flag in your step function'

        self.registry.append(Step(name, func, exit_codes))

    def register_cmd(self, name, cmd, exit_codes=(0, )):
        def func(dry_run=False):
            if not dry_run:
                return os.system(cmd)
            plain(f'Skipping: {cmd}')
        self.registry.append(Step(name, func(), exit_codes))

    def registered_step(self, name, exit_codes=(0, )):
        def wrapper(func):
            self.register(name, func, exit_codes)
            return func
        return wrapper

    @property
    def total_steps(self):
        return len(self.registry)

    def print_result(self, step_num, msg, exit_code, exit_codes):
        note(f'++ Step {step_num}/{self.total_steps}: ', newline=False)
        plain(msg.upper().strip(), newline=False)
        if isinstance(exit_code, int) in exit_codes:
            info(' succeeded')
        else:
            fail(f' failed, exit with code {exit_code}')
            sys.exit()

    def run(self, dry_run=False):
        info(self.registry_title)
        for ix, data in enumerate(self.registry):
            name, func, exit_codes = data
            exit_code = func(dry_run)
            self.print_result(ix, name, exit_code, exit_codes)



