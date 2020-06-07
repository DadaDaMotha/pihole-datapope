import os
import textwrap

import click

from pihole_datapope.cli import StepHandlerRegistry
from pihole_datapope.utils.file import ensure_file_and_content
from pihole_datapope.utils.network import inet_connected_iface


class InstallRaspiAP(StepHandlerRegistry):
    registry_title = "Installation Bridged AP for RasperriPi"


install = InstallRaspiAP()


@install.registered_step('Example Step')
def example_step(dry_run=False, sure=()):
    assert dry_run in (True, False)
    print('all ok')

# install.register_cmd('ls', 'Some Command')

# install.register_cmd('sudo apt install hostapd')
# install.register_cmd('sudo systemctl unmask hostapd')
# install.register_cmd('sudo systemctl enable hostapd')
#
#
# @install.registered_step('Create Bridge Network in /etc/systemd/network/')
# def create_bridge_network(inet_iface, bridge_name='br0', ap_iface='wlan0'):
#     network_p = '/etc/systemd/network/'
#     content = textwrap.dedent(f"""
#     [NetDev]
#     Name={bridge_name}
#     Kind=bridge""".lstrip())
#
#     ensure_file_and_content(
#         os.path.join(network_p, f'bridge-{bridge_name}.netdev'), content)
#
#     content_network = textwrap.dedent(f"""
#         [Match]
#         Name={inet_iface}
#
#         [Network]
#         Bridge={bridge_name}""".lstrip())
#     ensure_file_and_content(
#         os.path.join(network_p, f'{bridge_name}-member-{inet_iface}.network'),
#         content_network)
#     return 0
#
#
# install.register_cmd('sudo systemctl enable systemd-networkd')
#
# @install.registered_step('Define the bridge device IP configuration')
# def define_bridge_config():


@click.command()
@click.option('--bridge-name', default='br_datapope', required=True)
@click.option('--inet-iface', default=inet_connected_iface)
@click.option('--ap-iface', required=True, default='wlan0')
@click.option('--dry-run', is_flag=True, default=False)
def install_ap(bridge_name, inet_iface, ap_iface, dry_run):
    """ Install a bridged access point on a raspberryPi
    see https://www.raspberrypi.org/
     """
    install.run(dry_run=dry_run,
                bridge_name=bridge_name,
                inet_iface=inet_iface,
                ap_iface=ap_iface
                )
