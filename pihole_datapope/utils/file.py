import os
import re
import shutil

START_BLOCK = "### START MANAGED BY DATAPOPE"
END_BLOCK = "### END MANAGED BY DATAPOPE"
BACKUP_SUFIX = '.popebak'


class MissingEditBlockException(Exception):
    pass


def block_wrapped(func):
    def with_blocks(file, text, *args, **kwargs):
        return func(
            file, "\n".join((START_BLOCK, text, END_BLOCK)), *args, **kwargs)
    return with_blocks


@block_wrapped
def prepend_to(file, text, backup=False):
    if backup:
        backup_file(file)
    with open(file, 'r+') as f:
        s = f.read()
        f.seek(0)
        f.write(f"{text}\n{s}")


@block_wrapped
def insert_in(file, text, where, match_line=False, prepend=False,
              max_times=1, backup=True):
    """
    Insert content into a file at specific locations.
    Support only insert on new lines.

    filepath: pathlike
    text: content to insert
    at_occurrence: string/re pattern. If string, equals to `^string`
    match_line: use re.match to match the line exactly, else do a re.search
    prepend: switch between appending and prepending
    max_times: maximum times to do the operation
    backup: create a backup of the file

    """
    new_lines = []
    found = 0

    if isinstance(where, str):
        where = re.compile(where)

    re_search = where.match if match_line else where.search

    with open(file, 'r') as f:
        lines = f.read().split('\n')
    for line in lines:
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
        raise ValueError(f'{where} not found in {file}')

    if backup:
        backup_file(file)

    with open(file, 'w') as f:
        f.write("\n".join(new_lines))


@block_wrapped
def append_to(file, text, backup=False):
    if backup:
        backup_file(file)
    with open(file, "a") as f:
        f.write(text)


def containing(file, text):
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


def split_by_blocks(text):
    """ Only finds the first block and returns a tuple of 3 strings. """
    try:
        top, rest = text.split(START_BLOCK, 1)
        middle, last = rest.split(END_BLOCK, 1)
        return top, middle, last
    except ValueError:
        raise MissingEditBlockException


def ensure_content_in(file, content, prepend=False, where=None, backup=False):
    if not os.path.exists(file):
        touch(file)
        append_to(file, content)
    elif not containing(file, content):
        if where:
            insert_in(file, content,
                      prepend=prepend, where=where, backup=backup)
        if prepend:
            prepend_to(content, file, backup)
        else:
            append_to(content, file, backup)


def backup_file(fp):
    """ Copies a file with all possible metadata, see shutil.copy2. """
    dir, fn = os.path.split(fp)
    shutil.copy2(fp, os.path.join(dir, f"{fn}{BACKUP_SUFIX}"))


def touch(fname):
    if os.path.exists(fname):
        os.utime(fname, None)
    else:
        open(fname, 'a').close()
