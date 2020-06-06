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


def backup_file(fp):
    dir, fn = os.path.split(fp)
    shutil.copy2(fp, os.path.join(dir, f"{fn}.popebak"))


def ensure_packages(packages):
    missing = set(dep for dep in packages if not shutil.which(dep))
    if missing:
        raise FileNotFoundError(f'{", ".join(missing)} need to be installed')


def inet_connected_iface():
    return os.popen("route | grep '^default' | grep -o '[^ ]*$'").read().strip()


def append_to_file(file, text):
    with open(file, "a") as f:
        f.write(text)


def insert_in(filepath, text, after=True, at_occurrence=None, backup=True):
    if backup:
        backup_file(filepath)
    with open(filepath, "r+") as f:
        s = f.read()
        if not at_occurrence:
            f.seek(0)
            f.write(f"{text}\n" + s)
        else:
            raise NotImplementedError


def add_to_file(file, content, prepend=False, at_occurrence=None):
    """
    Add content either to end or beginning of file.
    If `at_occurrence_of` is specified, search line starting with that string,
    else use fallback.
    """
    if at_occurrence:
        pass

    if prepend:
        insert_in(file, content)
    else:
        append_to_file(file, content)


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


def ensure_file_and_content(file, content, prepend=False):
    if not os.path.exists(file):
        touch(file)
        append_to_file(file, content)
    elif not is_in_file(content, file):
        add_to_file(file, content, prepend)
