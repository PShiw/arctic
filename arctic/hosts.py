"""
Utilities to resolve a string to Mongo host, or a Arctic library.
"""
import ConfigParser
from ConfigParser import NoOptionError, NoSectionError
import os
import re
from weakref import WeakValueDictionary

from .logging import logger

__all__ = ['get_arctic_lib', 'get_arctic_for_library']



# Application environment variables
arctic_cache = WeakValueDictionary()


CONNECTION_STR = re.compile(r"(^\w+\.?\w+)@([^\s:]+:?\w+)$")


def get_arctic_lib(connection_string, **kwargs):
    """
    Returns a mongo library for the given connection string

    Parameters
    ---------
    connection_string: `str`
        Format must be one of the following:
            library@trading for known mongo servers
            library@hostname:port

    Returns:
    --------
    Arctic library
    """
    from .arctic import Arctic
    m = CONNECTION_STR.match(connection_string)
    if not m:
        raise ValueError("connection string incorrectly formed: %s" % connection_string)
    library, host = m.group(1), m.group(2)
    return _get_arctic(host, **kwargs)[library]


def _get_arctic(instance, **kwargs):
    # Consider any kwargs passed to the Arctic as discriminators for the cache
    key = instance, frozenset(kwargs.iteritems())

    # Don't create lots of Arctic instances
    arctic = arctic_cache.get(key, None)
    if not arctic:
        # Create the instance. Note that Arctic now connects
        # lazily so this doesn't connect until on creation.
        from .arctic import Arctic
        arctic = Arctic(instance, **kwargs)
        arctic_cache[key] = arctic
    return arctic