# coding: utf-8
import sys

if sys.version_info[0] == 3:
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError
else:
    from urllib import urlencode
    from urllib2 import HTTPError, Request, urlopen
