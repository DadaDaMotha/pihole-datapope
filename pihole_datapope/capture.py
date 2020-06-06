import shutil

# iface = 'eth0'
dependencies = ('tcpdump',)
GET_FILTER = "-s 0 -A 'tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420'"
POST_FILTER = "-s 0 -A 'tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504F5354'"
GET_INCOMING_443 = "-s 0 -A 'tcp dst port 443 and tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420'"
POST_INCOMING_443 = "-s 0 -A 'tcp dst port 443 and tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504F5354'"
# GET_INCOMING_80


def tcp_http_filter(methods=('GET',), in_ports=(80, 443), out_ports=()):
    """Constructs the filter expression for tcpdump to filter http traffic
    based on request method, either incoming traffic on ports `in_ports`
    or outgoing traffic in `out_ports`
    """
    to_bytes = dict(
        GET='0x47455420',
        POST='0x504F5354'
    )
    method_lookup = 'tcp[((tcp[12:1] & 0xf0) >> 2):4]'
    filters = []
    if all((in_ports, out_ports, in_ports == out_ports)):
        filters += [f"tcp port {p}" for p in in_ports]
    elif out_ports:
        filters += [f"tcp src port {p}" for p in out_ports]
    elif in_ports:
        filters += [f"tcp dst port {p}" for p in in_ports]
    for method in methods:
        filters.append(f"{method_lookup} = {to_bytes[method]}")

    all_filters = " and ".join(filters)
    return f"-s 0 -A '{all_filters}'"


def stream_dump(iface, to_file=None, limit=None, incoming=(80, 443), outgoing=(80, 443)):
    """

    Dump all GET requests arriving on the interface.

    Options
        -tttt: human readable timestamps
        -l: direct output
        --immediate-mode:
        -n: capture only IP address packets
        -c: limit dumps
        -s: snaplen, setting to 0 sets to default 262144
    """
    im = '--immediate-mode'
    options = [f'tcpdump -tttt -i {iface}']
    ports = (80, 443)
    if not to_file:
        options.append('-l')
    else:
        options.append(f'-w {to_file}')
    if limit:
        options.append(f' -c {limit}')
    filter = tcp_http_filter(in_ports=incoming, out_ports=outgoing)
    options.append(filter)
    return " ".join(options)

