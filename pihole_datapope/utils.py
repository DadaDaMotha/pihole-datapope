import os
import shutil
from urllib import parse


def url_parse(url):
    return parse.urlparse(url)


def ensure_packages(packages):
    missing = set(dep for dep in packages if not shutil.which(dep))
    if missing:
        raise FileNotFoundError(f'{", ".join(missing)} need to be installed')


def inet_connected_iface():
    return os.popen(
        "route | grep '^default' | grep -o '[^ ]*$'").read().strip()
