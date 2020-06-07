import os
import shutil
from urllib import parse


def url_parse(url):
    return parse.urlparse(url)


def ensure_packages(packages):
    missing = set(dep for dep in packages if not shutil.which(dep))
    if missing:
        raise FileNotFoundError(f'{", ".join(missing)} need to be installed')


def funcn(func):
    return func.__code__.co_name
