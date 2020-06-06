import binascii
# good examples:
# https://www.middlewareinventory.com/blog/tcpdump-capture-http-get-post-requests-apache-weblogic-websphere/

def fjoin(how, expressions):
    return f" {how} ".join(expressions).strip()


def four_long(string):
    assert len(string) <= 4
    return string + (4 - len(string)) * " "


def as_hex_bytes(string):
    return binascii.hexlify(string.encode('utf-8'))


def as_bytestring(method):
    """
    Return the string used for tcp_http_filter:
    e.g. 'GET ' will be '0x47455420'
    """
    s = str(as_hex_bytes(method))
    return "0" + s.upper().replace('B', 'x', 1).replace("'", "")


def tcp_http_filter(methods=('GET',), in_ports=(80, 443), out_ports=()):
    """Constructs the filter expression for tcpdump to filter http traffic
    based on request method, either incoming traffic on ports `in_ports`
    or outgoing traffic in `out_ports`
    """

    assert methods
    selector = 'tcp[((tcp[12:1] & 0xf0) >> 2):4]'
    by_port_dst = []

    if all((in_ports, out_ports, in_ports == out_ports)):
        by_port_dst += [f"tcp port {p}" for p in in_ports]
    elif out_ports:
        by_port_dst += [f"tcp src port {p}" for p in out_ports]
    elif in_ports:
        by_port_dst += [f"tcp dst port {p}" for p in in_ports]

    by_request_method = [
        f"{selector} = {as_bytestring(four_long(m))}" for m in methods
    ]

    joined_filters = fjoin('and', [
        fjoin('or', by_port_dst),
        fjoin('or', by_request_method)
    ])

    return f"-s 0 -A '{joined_filters}'"


def stream_dump(
    iface,
    to_file=None,
    limit=None,
    methods=('GET', ),
    incoming=(80, 443),
    outgoing=(80, 443)
):
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
    if not to_file:
        options.append('-l')
    else:
        options.append(f'-w {to_file}')
    if limit:
        options.append(f' -c {limit}')
    options.append(
        tcp_http_filter(methods=methods, in_ports=incoming, out_ports=outgoing)
    )
    return " ".join(options)
