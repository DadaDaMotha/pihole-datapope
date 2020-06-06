import os
import shutil
from urllib import parse


def url_parse(url):
    return parse.urlparse(url)


def touch(fname):
    if os.path.exists(fname):
        os.utime(fname, None)
    else:
        open(fname, 'a').close()

def ensure_packages(packages):
    missing = set(dep for dep in packages if not shutil.which(dep))
    if missing:
        raise FileNotFoundError(f'{", ".join(missing)} need to be installed')


def inet_connected_iface():
    return os.popen("route | grep '^default' | grep -o '[^ ]*$'").read().strip()


def append_to_file(file, text):
    with open(file, "a") as f:
        f.write(text)


def prepend_to_file(file, text):
    with open(file, "r+") as f:
        s = f.read()
        f.seek(0)
        f.write(f"{text}\n" + s)


def is_in_file(text, file):
    """Ensure exact string in file. Strip empty lines.
    Return true if matched, None if not matched.
    """
    with open(file, 'r') as f:
        lines = [ln.strip() for ln in f.readlines() if ln.strip()]

    text_lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
    match_start = None

    for ix, line in enumerate(lines):
        if line == text_lines[0]:
            match_start = ix
            break
    if match_start:
        s = match_start
        e = s + len(text_lines)
        subset = lines[s:e]
        if subset == text_lines:
            # matches the sequence
            return True
    return False
