from click.testing import CliRunner

from pihole_datapope.commands.datapope.install_ap import install_ap


class TestIntallAPCli:

    cli = install_ap

    def invoke(self, commands):
        return CliRunner().invoke(self.cli, commands)

    def test_running_at_all(self):
        result = self.invoke(['--help'])
        assert result.exit_code == 0
        assert '--help' in result.output

    def test_dry_drun(self):
        result = self.invoke([
        ])
        print(result.output)
        assert result.exit_code == 0
