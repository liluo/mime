# -*- coding: utf-8 -*-
import re
from glob import glob
from os.path import realpath, dirname, join
from .type import Type, Types
from .version import VERSION


DIR = dirname(realpath(__file__))
STARTUP = True

TEXT_FORMAT_RE = re.compile("""
    ([*])?                                             # 0: Unregistered?
    (!)?                                               # 1: Obsolete?
    (?:(\w+):)?                                        # 2: Platform marker
    (?:([-\w.+]+)\/([-\w.+]*))?                        # 3,4: Media type
    (?:\s+@([^\s]+))?                                  # 5: Extensions
    (?:\s+:((?:base64|7bit|8bit|quoted\-printable)))?  # 6: Encoding
    (?:\s+'(.+))?                                      # 7: URL list
    (?:\s+=(.+))?                                      # 8: Documentation
    (?:\s*([#].*)?)?
""", re.VERBOSE)


class MIMETypes(object):
    _types = Types(VERSION)

    def __repr__(self):
        return '<MIMETypes version:%s>' % VERSION

    @classmethod
    def load_from_file(cls, type_file):
        data = open(type_file).read()
        data = data.split('\n')
        mime_types = Types()
        for index, line in enumerate(data):
            item = line.strip()
            if not item:
                continue
            try:
                ret = TEXT_FORMAT_RE.match(item).groups()
            except Exception as e:
                __parsing_error(type_file, index, line, e)

            (unregistered, obsolete, platform, mediatype, subtype, extensions,
             encoding, urls, docs, comment) = ret
            if mediatype is None:
                if comment is None:
                    __parsing_error(type_file, index, line, RuntimeError)
                continue
            extensions = extensions and extensions.split(',') or []
            urls = urls and urls.split(',') or []
            mime_type = Type('%s/%s' % (mediatype, subtype))
            mime_type.extensions = extensions
            mime_type.encoding = encoding
            mime_type.system = platform
            mime_type.is_obsolete = bool(obsolete)
            mime_type.registered = (not unregistered)
            mime_type.docs = docs
            mime_type.url = urls
            mime_types.add(mime_type)
        return mime_types


def __parsing_error(filename, index, line, error):
    print("%s:%s: Parsing error in MIME type definitions." % (filename, index))
    print("=> %s" % line)
    raise error


def startup():
    global STARTUP
    if STARTUP:
        type_files = glob(join(DIR, 'types', '*'))
        type_files.sort()
        for type_file in type_files:
            MIMETypes.load_from_file(type_file)
    STARTUP = False

startup()
