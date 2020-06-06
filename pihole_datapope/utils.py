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
    return os.popen("route | grep '^default' | grep -o '[^ ]*$'").read().strip()


def ensure_in_file(text, file, prepend=False):
    """Ensure exact string in file.
    Either prepend or append text if missing.
    Return true if all is fine.
    """
    with open(file, 'r') as f:
        lines = [ln for ln in f.readlines() if ln]

    text_lines = [ln for ln in text.split('\n') if ln]
    match_start = None

    for ix, line in enumerate(lines):
        if not line:
            if line == text_lines[0]:
                match_start = ix
                break
    if match_start:
        s = match_start
        e = s + len(text_lines)
        subset = lines[s:e]
        if subset == text_lines:
            # matches the sequence
            return
