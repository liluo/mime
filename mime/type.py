# -*- coding: utf-8 -*-
import re
import sys
from collections import defaultdict
from itertools import chain


UNREG_RE = re.compile('[Xx]-', re.DOTALL)
ENCODING_RE = re.compile('(?:base64|7bit|8bit|quoted\-printable)', re.DOTALL)
PLATFORM_RE = re.compile(sys.platform, re.DOTALL)
MEDIA_TYPE_RE = re.compile('([-\w.+]+)\/([-\w.+]*)', re.DOTALL)

SIGNATURES = ('application/pgp-keys',
              'application/pgp',
              'application/pgp-signature',
              'application/pkcs10',
              'application/pkcs7-mime',
              'application/pkcs7-signature',
              'text/vcard')

RFC_URL = "http://rfc-editor.org/rfc/rfc%s.txt"
IANA_URL = "http://www.iana.org/assignments/media-types/%s/%s"
LTSW_URL = "http://www.ltsw.se/knbase/internet/%s.htp"
DRAFT_URL = "http://datatracker.ietf.org/public/idindex.cgi?command=id_details&filename=%s"
CONTACT_URL = "http://www.iana.org/assignments/contact-people.htm#%s"


class InvalidContentType(RuntimeError):
    pass


class Type(object):

    def __init__(self, content_type):
        matchdata = MEDIA_TYPE_RE.match(content_type)

        if matchdata is None:
            raise InvalidContentType('Invalid Content-Type provided "(%s)"' % content_type)

        self.content_type = content_type
        self.raw_media_type = matchdata
        self.raw_sub_type = matchdata

        self.simplified = self.simplify(self.content_type)

        self.extensions = []
        self.encoding = 'default'
        self.system = None
        self.registered = True
        self.url = None
        self.obsolete = None
        self.docs = None

    def __repr__(self):
        return '<MIME::Type %s>' % self.content_type

    def __eq__(self, other):
        pass

    def is_like(self, other):
        if hasattr(other, 'simplified'):
            simplified = other.simplified
        else:
            simplified = self.simplify(other)
        return self.simplified == simplified

    def priority_compare(self, other):
        pass

    @property
    def urls(self):
        pass

    @property
    def is_registered(self):
        pass

    @property
    def is_binary(self):
        # MIME types can be specified to be sent across a network in
        # particular
        # formats. This method returns +true+ when the MIME type
        # encoding is set
        # to <tt>base64</tt>.
        return self.encoding == 'base64'

    @property
    def is_ascii(self):
        # Returns +true+ when the simplified MIME type is in the list of known
        # digital signatures.
        pass

    @property
    def is_signature(self):
        # Returns +true+ when the simplified MIME type is in the list of
        # known
        # digital signatures.
        pass

    @property
    def is_system(self):
        # Returns +true+ if the MIME::Type is specific to an operating system.
        pass

    @property
    def is_platform(self):
        # Returns +true+ if the MIME::Type is specific to the current operating
        # system as represented by RUBY_PLATFORM.
        pass

    @property
    def is_complete(self):
        # Returns +true+ if the MIME::Type specifies an extension list,
        # indicating that it is a complete MIME::Type.
        pass

    @property
    def to_s(self):
        # Returns the MIME type as a string.
        return self.content_type

    @property
    def to_str(self):
        # Returns the MIME type as a string for implicit conversions.
        return self.content_type

    @property
    def to_a(self):
        # Returns the MIME type as an array suitable for use with
        # MIME::Type.from_array.
        pass

    @property
    def to_hash(self):
        # Returns the MIME type as an array suitable for use with
        # MIME::Type.from_hash.
        pass

    @classmethod
    def simplify(cls, content_type):
        matchdata = MEDIA_TYPE_RE.match(content_type)
        if matchdata is None:
            return None
        wrap = lambda s: re.sub(UNREG_RE, '', s.lower())
        (media_type, subtype) = matchdata.groups()
        return '%s/%s' % (wrap(media_type), wrap(subtype))

    @classmethod
    def from_array(*array):
        pass

    @classmethod
    def from_hash(hash):
        pass

    @classmethod
    def from_mime_type(mime_type):
        pass


class Types(object):
    """
    = MIME::Types
    MIME types are used in MIME-compliant communications, as in e-mail or
    HTTP traffic, to indicate the type of content which is transmitted.
    MIME::Types provides the ability for detailed information about MIME
    entities (provided as a set of MIME::Type objects) to be determined and
    used programmatically. There are many types defined by RFCs and vendors,
    so the list is long but not complete; don't hesitate to ask to add
    additional information. This library follows the IANA collection of MIME
    types (see below for reference).

    == Description
    MIME types are used in MIME entities, as in email or HTTP traffic. It is
    useful at times to have information available about MIME types (or,
    inversely, about files). A MIME::Type stores the known information about
    one MIME type.

    == Usage
     from mime import Type, Types

     plaintext = Types['text/plain']
     text = plaintext[0]
     print text.media_type            # => 'text'
     print text.sub_type              # => 'plain'

     print " ".join(text.extensions)  # => 'asc txt c cc h hh cpp'
     print text.encoding              # => 8bit
     print text.is_binary             # => False
     print text.is_ascii              # => True
     print text.is_obsolete           # => False
     print text.is_registered         # => True
     print text == 'text/plain'       # => True
     print Type.simplify('x-appl/x-zip') # => 'appl/zip'

    == About
    This module is built to conform to the MIME types of RFCs 2045 and 2231.
    It follows the official IANA registry at
    http://www.iana.org/assignments/media-types/ and
    ftp://ftp.iana.org/assignments/media-types with some unofficial types
    added from the the collection at
    http://www.ltsw.se/knbase/internet/mime.htp

    This is originally based on Perl MIME::Types by Mark Overmeer.
    This is Python clone of https://github.com/halostatue/mime-types

    Licence:  MIT Licence
    See Also:
        http://www.iana.org/assignments/media-types/
        http://www.ltsw.se/knbase/internet/mime.htp
    """

    TYPES = []
    _types = set()
    type_veriants = defaultdict(list)
    extension_index = defaultdict(list)

    def __init__(self, data_version=None):
        self.data_version = data_version

    def __repr__(self):
        return '<MIME::Types version:%s>' % self.data_version

    def __getitem__(self, type_id):  # flags={}
        pass

    @classmethod
    def add_type_variant(cls, mime_type):
        cls.type_veriants[mime_type.simplified].append(mime_type)

    @classmethod
    def index_extensions(cls, mime_type):
        for ext in mime_type.extensions:
            cls.extension_index[ext].append(mime_type)

    @property
    def defined_types(self):
        return chain(*self.type_veriants.values())

    @property
    def count(self):
        return len(list(self.defined_types))

    def each(self, block):
        return map(block, self.defined_types)

    def type_for(self, filename, platform=False):
        pass

    of = type_for

    @classmethod
    def add(cls, *types):
        for mime_type in types:
            if isinstance(mime_type, Types):
                cls.add(*mime_type.defined_types)
            else:
                mts = cls.type_veriants.get(mime_type.simplified)
                if mts and mime_type in mts:
                    Warning('Type %s already registered as a variant of %s.',
                            mime_type, mime_type.simplified)
                cls.add_type_variant(mime_type)
                cls.index_extensions(mime_type)
