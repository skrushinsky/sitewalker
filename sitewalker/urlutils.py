
'''
urlutils.py - URL utilities.
'''
from urllib.parse import urlparse, urlunparse, unquote
import re
import logging

__author__ = 'Sergey Krushinsky'
__copyright__ = "Copyright 2018"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "krushinsky@gmail.com"

_collapse = re.compile('([^/]+/\.\./?|/\./|//|/\.$|/\.\.$|^\.)')
_server_authority = re.compile('^(?:([^\@]+)\@)?([^\:]+)(?:\:(.+))?$')
_default_port = {
    'http': 80,
    'https': 443,
    'gopher': 70,
    'news': 119,
    'snews': 563,
    'nntp': 119,
    'snntp': 563,
    'ftp': 21,
    'telnet': 23,
    'prospero': 191,
}
_relative_schemes = [
    'http', 'https', 'news', 'snews', 'nntp', 'snntp', 'ftp', 'file', '']
_server_authority_schemes = ['http', 'https', 'news', 'snews', 'ftp',]


def norm(url, domain=None):
    """
    Normalize URL.

    Based on http://github.com/jehiah/urlnorm library, adapted to Python 3
    with some fixes and modifications.
    Actions:

    1. Converts relative URLs to absolute.
    2. If protocol is missing, uses 'http'.
    3. Normalizes cases.
    4. Removes default port.
    5. Collapses (optimizes) path.
    6. Unquotes path fragments.
    7. Converts international domains from idna to utf8.
    8. Removes fragment, if any.
    9. Removes 'www' prefix, if any

    Arguments:
        url : URL address, a string
        domain : default domain, used if netloc is missing, i.e. the URL is relative

    Returns:
        a tuple of values compatiable with urllib.parse.urlparse result.

    Fails with AssertionError if a relative URL can not be converted to absolute.
    This happens when neither URL contains netloc, nor domain parameter is provided.
    """
    (scheme, authority, path, parameters, query, fragment) = urlparse(url, scheme='http')
    #logging.debug(pprint.pformat((scheme, authority, path, parameters, query, fragment) ))
    if not authority:
        authority = domain
    assert authority, '%s: No authority!' % url
    userinfo, host, port = _server_authority.match(authority).groups()
    if host[-1] == '.':
        host = host[:-1]
    authority = host.lower()
    if userinfo:
        authority = "%s@%s" % (userinfo, authority)
    if port and int(port) != _default_port.get(scheme, None):
        authority = "%s:%s" % (authority, port)

    if scheme in _relative_schemes:
        last_path = path
        while 1:
            path = _collapse.sub('/', path, 1)
            if last_path == path:
                break
            last_path = path

    path = unquote(path)
    if path == '':
        path = '/'	
    try:
        authority = authority.encode('utf8').decode('idna')
    except Exception as ex:
        logging.warn(ex)

    parts = (scheme, authority, path, parameters, query, '')
    return parts

def join_parts(url):
    """Convert norm result to string."""
    return urlunparse(url)

def get_domain(url):
    """Given an URL, return domain name."""
    return urlparse(url)[1]

def remove_params(url):
    # remove parameters and query: we don't need them for site map
    return url[:3] + ('', '', '')


def belongs_to_domain(url, domain):
    '''Check, if url belongs to domain.
    www prefix is ignored, i.e 'www.python.org' = 'python.org'
    '''
    d = url[1]
    if d.startswith('www.'):
        d = d[4:]	
    if domain.startswith('www.'):
        domain = domain[4:]	

    return d == domain	