import binascii
# good examples: https://www.middlewareinventory.com/blog/tcpdump-capture-http-get-post-requests-apache-weblogic-websphere/


def fjoin(how, expressions):
    return f" {how} ".join(expressions).strip()


def as_hex_bytes(string):
    return binascii.hexlify(string.encode('utf-8'))


def as_bytestring(method):
    """
    Return the string used for tcp_http_filter:
    e.g. 'GET ' will be '0x47455420'
    """
    return "0x" + str(int(as_hex_bytes(method)))


def tcp_http_filter(methods=('GET',), in_ports=(80, 443), out_ports=()):
    """Constructs the filter expression for tcpdump to filter http traffic
    based on request method, either incoming traffic on ports `in_ports`
    or outgoing traffic in `out_ports`
    """

    method_lookup = 'tcp[((tcp[12:1] & 0xf0) >> 2):4]'
    or_filters = []

    if all((in_ports, out_ports, in_ports == out_ports)):
        or_filters += [f"tcp port {p}" for p in in_ports]
    elif out_ports:
        or_filters += [f"tcp src port {p}" for p in out_ports]
    elif in_ports:
        or_filters += [f"tcp dst port {p}" for p in in_ports]

    method_f = [f"{method_lookup} = {as_bytestring(m)}" for m in methods]

    joined_filters = fjoin('and', [
        fjoin('or', or_filters),
        fjoin('or', method_f)
    ])

    return f"-s 0 -A '{joined_filters}'"


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
    options.append(
        tcp_http_filter(in_ports=incoming, out_ports=outgoing)
    )
    return " ".join(options)
