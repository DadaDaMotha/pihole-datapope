import os
import sys
from collections import namedtuple
from inspect import signature
from math import ceil

import click

from pihole_datapope.utils import funcn


def format_message(message, api):
    return message


def plain(msg, api=None, newline=True, bold=True):
    click.secho(format_message(msg, api), nl=newline, fg='white', bold=bold)


def info(msg, api=None, newline=True, bold=False):
    click.secho(format_message(msg, api), nl=newline, fg='green', bold=bold)


def warn(msg, api=None, newline=True, bold=False):
    click.secho(format_message(msg, api), nl=newline, fg='yellow', bold=bold)


def fail(msg, api=None, newline=True, err=False, bold=False):
    click.secho(
        format_message(msg, api), nl=newline, fg='red', err=err, bold=bold)


def note(msg, api=None, newline=True):
    click.secho(format_message(msg, api), nl=newline, fg='cyan')


Step = namedtuple('Step', ('name', 'func', 'exit_codes'))


class StepHandlerRegistry(object):

    tty_width = 79
    fill_symbol = '-'

    cmd_handler = os.system

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
        """Register a simple command to execute with
        cmd_handler. These commands are not expected to return system
        output, but a status code.
        """
        self.registry.append(Step(name or cmd, cmd, exit_codes))

    def registered_step(self, name, exit_codes=(0, )):
        def wrapper(func):
            self.register(func, name, exit_codes)
            return func
        return wrapper

    @property
    def total_steps(self):
        return len(self.registry)

    def step_result(self, step_num, msg, exit_code, exit_codes, nl=True):
        note(f'+ {step_num}/{self.total_steps}: '.upper(), newline=False)
        if isinstance(exit_code, int) and exit_code in exit_codes:
            info('[✔] succeeded ', newline=False)
        else:
            fail(f'[✘] failed, exit {exit_code} ', newline=False)
            plain(msg.strip())
            sys.exit()
        plain(msg.strip(), newline=nl)

    def run(self, ask_each_step=False, dry_run=False, **kwargs):
        if not self.registry:
            fail('Can not run with empty registry')
            sys.exit()

        if dry_run:
            info(self.section_title('using dry run option '.upper()))

        with click.progressbar(
            self.registry, length=self.total_steps,
            label=self.registry_title.upper()
        ) as bar:
            for ix, step in enumerate(bar, 1):
                if ask_each_step:
                    wants = click.confirm(
                        f'Do Step {ix}: {step.name}?')
                    if not wants:
                        continue
                self._do_step(ix, step, dry_run, **kwargs)

    def _do_step(self, ix, step, dry_run, **kwargs):
        # use matched kwargs for the function
        simple_cmd = not callable(step.func)
        func_kwargs = self.bindable_kwargs(
            step.func, {**kwargs, 'dry_run': dry_run}
        ) if not simple_cmd else {}

        if dry_run:
            msg = self.func_repr(step.func)
            self.step_result(ix, msg, 0, [0], nl=not func_kwargs)
            if func_kwargs:
                plain(f"; Params: {str(func_kwargs)}")
            return func_kwargs
        self.step_result(
            ix,
            step.name,
            self.cmd_handler(step.func) if simple_cmd
            else step.func(**func_kwargs),
            step.exit_codes
        )
        return func_kwargs

    def section_title(self, title):
        to_fill = self.tty_width - len(title.strip()) - 2
        fill = ceil(to_fill / 2) * self.fill_symbol
        return f"{fill} {title} {fill}"[0:self.tty_width]

    @staticmethod
    def bindable_kwargs(func, dict_):
        return {n: dict_[n] for n in dict_ if n in signature(func).parameters}

    def func_repr(self, func):
        if not callable(func):
            return str(func)
        kwargs = [str(v) for v in signature(func).parameters.values()]
        return f"{funcn(func)}({', '.join(kwargs)})"

    def repeat(self, number):
        step = self.registry[number]
        self.step_result(number, step.name, step.func(), step.exit_codes)

    def interactive_edit(self, string_or_file):
        if os.path.isfile(string_or_file):
            return click.edit(filename=string_or_file)
        return click.edit(string_or_file)
