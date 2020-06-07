import os
import textwrap

import click

from pihole_datapope.cli import StepHandlerRegistry
from pihole_datapope.utils.file import ensure_file_and_content


class InstallRaspiAP(StepHandlerRegistry):
    registry_title = "Installation Bridged AP for RasperriPi"


install = InstallRaspiAP()

install.register_cmd('sudo apt install hostapd')
install.register_cmd('sudo systemctl unmask hostapd')
install.register_cmd('sudo systemctl enable hostapd')


@install.registered_step('Create Bridge Network in /etc/systemd/network/')
def create_bridge_network(inet_iface, bridge_name='br0', ap_iface='wlan0'):
    network_p = '/etc/systemd/network/'
    fn = os.path.join(network_p, f'bridge-{bridge_name}.netdev')
    content = textwrap.dedent(f"""
            [NetDev]
            Name={bridge_name}
            Kind=bridge""")

    ensure_file_and_content(fn, content)

    fn_network = f'{bridge_name}-member-{inet_iface}.network'

    content_network = textwrap.dedent(f"""
        [Match]
        Name={inet_iface}

        [Network]
        Bridge={bridge_name}
    """)
    ensure_file_and_content(
        os.path.join(network_p, fn_network), content_network)


install.register_cmd('sudo systemctl enable systemd-networkd')


@click.command()
def install_ap():
    """ Install a bridged access point on a raspberryPi
    see https://www.raspberrypi.org/

                                     +- RPi -------+
                                 +---+ Bridge      |
                                 |   | WLAN AP     +-)))
                                 |   | 192.168.1.2 |         +- Laptop ----+
                                 |   +-------------+     (((-+ WLAN Client |
             +- Router ----+     |                           | 192.168.1.5 |
             | Firewall    |     |   +- PC#2 ------+         +-------------+
    Inet-WAN-+ DHCP server +-LAN-+---+ 192.168.1.3 |
             | 192.168.1.1 |     |   +-------------+
             +-------------+     |
                                 |   +- PC#1 ------+
                                 +---+ 192.168.1.4 |
                                     +-------------+
     """
    pass
