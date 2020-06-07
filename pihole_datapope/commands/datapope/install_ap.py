import os
import textwrap

import click

from pihole_datapope.cli import StepHandlerRegistry, info, plain
from pihole_datapope.utils.file import ensure_content_in, append_to
from pihole_datapope.utils.network import inet_connected_iface
from pihole_datapope.utils.random import random_password


class InstallRaspiAP(StepHandlerRegistry):
    registry_title = "Installation Bridged AP for RasperriPi"


install = InstallRaspiAP()

install.register_cmd('sudo apt install hostapd')
install.register_cmd('sudo systemctl unmask hostapd')
install.register_cmd('sudo systemctl enable hostapd')


@install.registered_step('Create Bridge Network in /etc/systemd/network/')
def create_bridge_network(inet_iface, br_iface='br0', ap_iface='wlan0'):
    network_p = '/etc/systemd/network/'
    content = textwrap.dedent(f"""
    [NetDev]
    Name={br_iface}
    Kind=bridge""".lstrip())

    ensure_content_in(
        os.path.join(network_p, f'bridge-{br_iface}.netdev'), content)

    content_network = textwrap.dedent(f"""
        [Match]
        Name={inet_iface}

        [Network]
        Bridge={br_iface}""".lstrip())
    ensure_content_in(
        os.path.join(network_p, f'{br_iface}-member-{inet_iface}.network'),
        content_network)
    return 0


install.register_cmd('sudo systemctl enable systemd-networkd')


@install.registered_step('Define the bridge device IP configuration')
def define_bridge_config(inet_iface, ap_iface, br_iface):
    file = '/etc/dhcpcd.conf'
    ensure_content_in(
        file,
        content=f'denyinterfaces {inet_iface} {ap_iface}',
        prepend=True,
        where='^interface',
        backup=True
    )
    append_to(file, f'interface {br_iface}')
    return 0


install.register_cmd('sudo rfkill unblock wlan')


@install.registered_step('Configure hostapd')
def configure_hostapd(ssid, passw, channel):
    file = '/etc/hostapd/hostapd.conf'
    assert len(passw) > 7

    content = textwrap.dedent(f"""
        country_code=GB
        interface=wlan0
        bridge=br0
        ssid={ssid}
        hw_mode=g
        channel={channel}
        macaddr_acl=0
        auth_algs=1
        ignore_broadcast_ssid=0
        wpa=2
        wpa_passphrase={passw}
        wpa_key_mgmt=WPA-PSK
        wpa_pairwise=TKIP
        rsn_pairwise=CCMP
    """)
    ensure_content_in(file, content, backup=True)


@click.command()
@click.option('--br-iface', default='br_datapope', required=True)
@click.option('--inet-iface', default=inet_connected_iface)
@click.option('--ap-iface', required=True, default='wlan0')
@click.option('--ssid', required=True, default='datapope-ap')
@click.option('--channel', required=True, default=7, type=int)
@click.option('--passw')
@click.option('--dry-run', is_flag=True, default=False)
def install_ap(br_iface, inet_iface, ap_iface, ssid, channel, passw, dry_run):
    """ Install a bridged access point on a raspberryPi
    see https://www.raspberrypi.org/
     """
    used_passw = passw or random_password()
    install.run(dry_run=True,
                br_iface=br_iface,
                inet_iface=inet_iface,
                ap_iface=ap_iface,
                ssid=ssid,
                passw=used_passw,
                channel=channel
                )
    if not passw:
        info(f'\n\n Password for {ssid}: ', newline=False)
        plain(used_passw + '\n')
