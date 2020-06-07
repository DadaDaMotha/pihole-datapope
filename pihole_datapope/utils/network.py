import os


def inet_connected_iface():
    return os.popen(
        "route | grep '^default' | grep -o '[^ ]*$'").read().strip()
