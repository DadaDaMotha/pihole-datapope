import os
import shutil
import tempfile

import pytest


def touch(fname):
    if os.path.exists(fname):
        os.utime(fname, None)
    else:
        open(fname, 'a').close()


@pytest.fixture
def temporary_directory():
    directory = tempfile.mkdtemp()
    yield directory
    shutil.rmtree(directory, ignore_errors=True)


@pytest.fixture
def temp_file(temporary_directory):
    fp = os.path.join(temporary_directory, 'temp_file')

    def create_temp_file(content=None):
        if not content:
            touch(fp)
        else:
            with open(fp, 'w') as f:
                f.write(content)
        return fp
    return create_temp_file
