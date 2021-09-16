# coding: utf-8
from __future__ import absolute_import, unicode_literals
from .client import Pasargad, ApiError


def get_version():
    return '.'.join(map(str, VERSION))


VERSION = (0, 1, 1)
__version__ = get_version()
