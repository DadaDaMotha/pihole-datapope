import logging
import os
import sys
import textwrap
import click

source_dir = os.path.join(os.path.dirname(__file__))
packages_folder = os.path.join(source_dir, 'commands')


class CLI(click.MultiCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def default_log_level(self):
        raise NotImplementedError

    @property
    def plugin_folder(self):
        raise NotImplementedError

    def filename_to_command(self, filename):
        return filename.replace('.py', '').replace('_', '-')

    def command_to_filename(self, command):
        return '{}.py'.format(command.replace('-', '_'))

    def list_commands(self, ctx):
        commands = []

        for filename in os.listdir(self.plugin_folder):
            if filename.startswith('__'):
                continue
            if filename.endswith('.py'):
                commands.append(self.filename_to_command(filename))
        commands.sort()

        return commands

    def get_command(self, ctx, command):
        ns = {}
        fn = os.path.join(
            self.plugin_folder, self.command_to_filename(command)
        )

        if not os.path.exists(fn):
            return

        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)

        function_name = self.command_to_filename(command).replace('.py', '')
        cli = ns[function_name]

        cli = click.option(
            '--debug', help='Adds lots of debug output',
            is_flag=True, is_eager=True, expose_value=False,
            callback=self.enable_debugging,
        )(cli)

        cli = click.option(
            '--post-mortem', help='Enable post-mortem debugging',
            is_flag=True, is_eager=True, expose_value=False,
            callback=self.enable_post_mortem,
        )(cli)

        return cli

    def enable_debugging(self, ctx, option, enable):
        if enable:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=self.default_log_level)

            # hide requests api logging by default
            logging.getLogger('requests').setLevel(logging.WARN)

    def enable_post_mortem(self, ctx, option, enable):
        def hook(type, value, tb):

            if hasattr(sys, 'ps1') or not sys.stderr.isatty():
                # we are in interactive mode or we don't have a tty-like
                # device, so we call the default hook
                sys.__excepthook__(type, value, tb)
            else:
                import traceback
                # we are NOT in interactive mode, print the exception...
                traceback.print_exception(type, value, tb)
                print()
                # ...then start the debugger in post-mortem mode.
                try:
                    from ipdb import ipdb
                    ipdb.post_mortem(tb)
                except ImportError:
                    import pdb
                    pdb.post_mortem(tb)

        if enable:
            sys.excepthook = hook


class DataPopeCli(CLI):
    default_log_level = logging.INFO
    plugin_folder = os.path.join(
        os.path.dirname(__file__), 'commands/datapope'
    )


@click.command(cls=DataPopeCli, help=textwrap.dedent("""
    datapope is a log scrambler for pihole logs.
    It's intention was to create a customized and enriched
    stream of your own activities, that makes it easy know,
    what news sites you visited, if when and where you watched
    documentaries.

    """))
@click.version_option(
    prog_name=u"Datapope for Pihole", message='%(prog)s %(version)s')
def datapope_cli():
    pass
