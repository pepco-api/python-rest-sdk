# coding: utf-8
import sys

if sys.version_info[0] == 3:
    from urllib.parse import urlencode
    from urllib.request import HTTPError, Request, urlopen
else:
    from urllib import urlencode
    from urllib2 import HTTPError, Request, urlopen
