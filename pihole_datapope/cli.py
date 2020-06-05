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


def listing(options):
    if isinstance(options, list) or isinstance(options, tuple):
        for i in options:
            plain(f'-- {i}\n')
    elif isinstance(options, dict):
        for key, val in options.items():
            plain(f'-- {key}:')
            if isinstance(val, list) or isinstance(val, tuple):
                for i in val:
                    plain(f'---- {i}\n')
            else:
                plain(str(val))

def server_title(name):
    line_length = 30
    c = 10
    r = line_length - c - len(name) - len(' [] ')
    note(f'{c * "-"} [{name}] {r * "-"}')


def adapter_title(name):
    line_length = 30
    c = 7
    r = line_length - c - len(name) - len(' Interface  ')
    info(f'{c * "-"} Interface {name} {r * "-"}')
