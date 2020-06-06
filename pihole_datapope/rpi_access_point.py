"""
https://www.raspberrypi.org/documentation/configuration/wireless/access-point-bridged.md

                                         +- RPi -------+
                                     +---+ Bridge      |
                                     |   | WLAN AP     +-)))
                                     |   | 192.168.1.2 |         +- Laptop ----+
                                     |   +-------------+     (((-+ WLAN Client |
                 +- Router ----+     |                           | 192.168.1.5 |
                 | Firewall    |     |   +- PC#2 ------+         +-------------+
(Internet)---WAN-+ DHCP server +-LAN-+---+ 192.168.1.3 |
                 | 192.168.1.1 |     |   +-------------+
                 +-------------+     |
                                     |   +- PC#1 ------+
                                     +---+ 192.168.1.4 |
                                         +-------------+
"""
import os
import textwrap

from pihole_datapope.utils import inet_connected_iface

dependecies = ('hostapd', )
enable_hostapd = 'sudo systemctl unmask hostapd && sudo systemctl enable hostapd'


def create_bridge_network(name='br0', path='/etc/systemd/network/'):
    fn = os.path.join(path, f'bridge-{name}.netdev')
    content = textwrap.dedent(f"""
        [NetDev]
        Name={name}
        Kind=bridge""")
    inet_iface = inet_connected_iface()
    ap_iface = ''
    fn_network = f'{name}-member-{inet_iface}.network'
    fn_network_path = '/etc/systemd/network/'

    content_network = textwrap.dedent(f"""
        [Match]
        Name={inet_iface}

        [Network]
        Bridge={name}
    """)
