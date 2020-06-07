import os
import sys
from collections import namedtuple
from inspect import signature

import click


def format_message(message):
    return message


def plain(msg, api=None, newline=True):
    click.secho(format_message(msg), nl=newline, fg='white')


def info(msg, api=None, newline=True):
    click.secho(format_message(msg), nl=newline, fg='green')


def warn(msg, api=None, newline=True):
    click.secho(format_message(msg), nl=newline, fg='yellow')


def fail(msg, api=None, newline=True):
    click.secho(format_message(msg), nl=newline, fg='red')


def note(msg, api=None, newline=True):
    click.secho(format_message(msg), nl=newline, fg='cyan')


Step = namedtuple('Step', ('name', 'func', 'exit_codes'))


class StepHandlerRegistry(object):

    def __init__(self):
        # Here we see why we use python 3: dicts are ordered!
        self.registry = []

    @property
    def registry_title(self):
        raise NotImplementedError

    def register(self, func, name, exit_codes=(0, )):
        """Registers a step."""
        assert name not in self.registry, "Can't register name twice"
        # assert 'dry_run' in signature(func).parameters, \
        #     'Implement a dry_run flag in your step function'

        self.registry.append(Step(name, func, exit_codes))

    def register_cmd(self, cmd, name=None, exit_codes=(0, )):
        def func(dry_run=False):
            if not dry_run:
                return os.system(cmd)
            plain(f'Skipping: {cmd}')
        self.registry.append(Step(name or cmd, func, exit_codes))

    def registered_step(self, name, exit_codes=(0, )):
        def wrapper(func):
            self.register(func, name, exit_codes)
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

    def run(self, ask_each_step=False, dry_run=False, interactive=True,
            **kwargs):
        if interactive:
            self.run_interactively()
            return
        with click.progressbar(
            self.registry, length=self.total_steps,
            label=self.registry_title.upper()
        ) as bar:
            for ix, step in enumerate(bar):
                if ask_each_step:
                    wants = click.confirm(
                        f'Do Step {ix}: {step.name}?')
                    if not wants:
                        continue
                # use matched kwargs for the function
                params = signature(step.func).parameters
                if dry_run:
                    plain(str(params))
                    continue
                exit_code = step.func(dry_run)
                self.print_result(
                    ix, step.name, exit_code, step.exit_codes
                )

    def repeat(self, number):
        step = self.registry[number]
        self.print_result(number, step.name, step.func(), step.exit_codes)
