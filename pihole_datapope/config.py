import os
from functools import lru_cache

config_path = os.path.expanduser('~/.datapope_config')
query_db_path = '/etc/pihole/pihole-FTL.db'

msg = """
    Create a config file in ~/.datapope_config with
    the following content:

    pihole_ip = 192.168.179.20
    database = sqlite|postgres
    ssh_user = optional
    ssh_port = optional, defaults 22

    Create the file
        echo "pihole_ip = 192.168.0.10" > ~/.datapope_config

"""


def ensure_user_configuration():
    if not os.path.isfile(config_path):
        raise FileNotFoundError(msg)


def tokenize(line):
    return tuple(t.strip() for t in line.split('='))


@lru_cache(maxsize=20)
def read_config():
    ensure_user_configuration()
    with open(config_path, 'r') as f:
        lines = f.readlines()
    return dict(tokenize(line) for line in lines)


def copy_query_db():
    ip = read_config()['pihole_ip']
    user = read_config().get('ssh_user')
    port = int(read_config().get('ssh_port'))
    cmd = f'scp -P {port or 22}{user}@{ip}:{query_db_path} /tmp/'
    return os.system(cmd)
