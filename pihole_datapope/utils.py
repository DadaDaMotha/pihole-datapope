import os
import re
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


def insert_in(filepath, text, at_occurrence, match_line=False, prepend=False, max_times=1, backup=True):
    """
    Insert content into a file at specific locations.
    Support only insert on new lines.

    filepath: pathlike
    text: content to insert
    at_occurrence: string/re pattern. If string, equals to `^string`
    match_line: use re.match to match the line exactly, otherwise just do a re.search
    prepend: switch between appending and prepending
    max_times: maximum times to do the operation
    backup: create a backup of the file

    """
    new_lines = []
    found = 0

    if isinstance(at_occurrence, str):
        at_occurrence = re.compile(at_occurrence)

    re_search = at_occurrence.match if match_line else at_occurrence.search

    with open(filepath, "r") as f:
        lines = f.readlines()
    for ix, line in enumerate(lines):
        if not line.strip():
            new_lines.append(line)
            continue
        if max_times and found < max_times:
            if re_search(line):
                found += 1
                new_lines += [text, line] if prepend else [line, text]
        else:
            new_lines.append(line)

    if not found:
        raise ValueError(f'{at_occurrence} not found in {filepath}')

    if backup:
        backup_file(filepath)

    with open(filepath, 'w') as f:
        f.write("\n".join(new_lines))


def is_in_file(text, file):
    """Ensure exact string in file. Strip empty lines.
    Returns on line number where text was found or 0.
    """
    with open(file, 'r') as f:
        lines = f.read().split('\n')

    match_start = None
    text = text.strip()
    text_split = text.split('\n')
    first_entry = text_split[0].strip()

    for ix, line in enumerate(lines, 1):
        if not line.strip():
            continue
        if line == first_entry:
            match_start = ix
            break
    if match_start:
        s = match_start - 1
        e = s + len(text_split)
        subset = lines[s:e]
        if subset == text_split:
            return match_start
    return 0


def ensure_file_and_content(file, content, prepend=False):
    if not os.path.exists(file):
        touch(file)
        append_to_file(file, content)
    elif not is_in_file(content, file):
        add_to_file(file, content, prepend)
