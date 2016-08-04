# -*- coding: utf-8 -*-
from future.utils import with_metaclass
from future.utils import iteritems, itervalues
import re
import sys
from collections import defaultdict
from itertools import chain
from copy import deepcopy


PLATFORM = sys.platform
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
REGEX_URLS = {'^RFC(\d+)$': RFC_URL, '^DRAFT:(.+)$': DRAFT_URL, '^\[([^\]]+)\]': CONTACT_URL}

if sys.version_info[0] == 3:
    basestring = str
    def cmp(x,y):
        if isinstance(x, Type): return x.__cmp__(y)
        if isinstance(y, Type): return y.__cmp__(x) * -1
        return 0 if x == y else (1 if x > y else -1)

def flatten(l):
    if isinstance(l, (list, tuple)):
        return [e for i in l for e in flatten(i)]
    return [l]


class InvalidContentType(RuntimeError):
    pass


class Type(object):
    """
    Builds a MIME::Type object from the provided MIME Content Type value
    (e.g., 'text/plain' or 'applicaton/x-eruby'). The constructed
    object is yielded to an optional block for additional configuration,
    such as associating extensions and encoding information.
    """
    def __init__(self, content_type):
        if content_type is None:
            raise InvalidContentType('Invalid Content-Type provided "(%s)"' % content_type)

        matchdata = MEDIA_TYPE_RE.match(content_type)
        if matchdata is None:
            raise InvalidContentType('Invalid Content-Type provided "(%s)"' % content_type)

        # content_type
        #   Returns the whole MIME content-type string.
        #   text/plain        => text/plain
        #   x-chemical/x-pdb  => x-chemical/x-pdb
        self.content_type = content_type

        # raw_media_type
        #   Returns the media type of the unmodified MIME type.
        #   text/plain        => text
        #   x-chemical/x-pdb  => x-chemical
        #
        # raw_sub_type
        #   Returns the media type of the unmodified MIME type.
        #   text/plain        => plain
        #   x-chemical/x-pdb  => x-pdb
        (self.raw_media_type, self.raw_sub_type) = matchdata.group(1, 2)

        # simplified
        #   The MIME types main- and sub-label can both start with <tt>x-</tt>,
        #   which indicates that it is a non-registered name. Of course, after
        #   registration this flag can disappear, adds to the confusing
        #   proliferation of MIME types. The simplified string has the <tt>x-</tt>
        #   removed and are translated to lowercase.
        #   text/plain        => text/plain
        #   x-chemical/x-pdb  => chemical/pdb
        self.simplified = self.simplify(self.content_type)

        # media_type
        #   Returns the media type of the simplified MIME type.
        #   text/plain        => text
        #   x-chemical/x-pdb  => chemical
        #
        # sub_type
        #   Returns the sub-type of the simplified MIME type.
        #   text/plain        => plain
        #   x-chemical/x-pdb  => pdb
        (self.media_type, self.sub_type) = MEDIA_TYPE_RE.match(self.simplified).group(1, 2)

        # The list of extensions which are known to be used for this MIME::Type.
        # Non-array values will be coerced into an array with #to_a. Array
        # values will be flattened and +nil+ values removed.
        self._extensions = []
        self._encoding = 'default'
        self._system = None
        self.registered = True

        # The encoded URL list for this MIME::Type. See #urls for more information.
        self.url = None
        self.is_obsolete = False
        self._docs = ''
        self._use_instead = None

    def __repr__(self):
        return '<MIME::Type %s>' % self.content_type

    def __str__(self):
        return self.content_type

    def __cmp__(self, other):
        """
        Compares the MIME::Type against the exact content type or the
        simplified type (the simplified type will be used if comparing against
        something that can be treated as a String). In comparisons,
        this is done against the lowercase version of the MIME::Type.
        """
        if hasattr(other, 'content_type'):
            return cmp(self.content_type.lower(), other.content_type.lower())
        elif isinstance(other, basestring):
            return cmp(self.simplified, self.simplify(str(other)))
        else:
            return cmp(self.content_type.lower(), other.lower())

    def __lt__(self, other):
        if hasattr(other, 'content_type'):
            return cmp(self.content_type.lower(), other.content_type.lower()) < 0
        elif isinstance(other, basestring):
            return cmp(self.simplified, self.simplify(str(other))) < 0
        else:
            return cmp(self.content_type.lower(), other.lower()) < 0

    def __gt__(self, other):
        if hasattr(other, 'content_type'):
            return cmp(self.content_type.lower(), other.content_type.lower()) > 0
        elif isinstance(other, basestring):
            return cmp(self.simplified, self.simplify(str(other))) > 0
        else:
            return cmp(self.content_type.lower(), other.lower()) > 0

    def __eq__(self, other):
        """
        Returns +true+ if the other object is a MIME::Type and the content
        types match.
        """
        return isinstance(other, self.__class__) and cmp(self, other) == 0

    def is_like(self, other):
         # Returns +true+ if the simplified type matches the current
        if hasattr(other, 'simplified'):
            return self.simplified == other.simplified
        else:
            return self.simplified == self.simplify(other)

    def priority_compare(self, other):
        """
        Compares the MIME::Type based on how reliable it is before doing a
        normal <=> comparison. Used by MIME::Types#[] to sort types. The
        comparisons involved are:
        1. self.simplified <=> other.simplified (ensures that we
           don't try to compare different types)
        2. IANA-registered definitions < other definitions.
        3. Generic definitions < platform definitions.
        3. Complete definitions < incomplete definitions.
        4. Current definitions < obsolete definitions.
        5. Obselete with use-instead references < obsolete without.
        6. Obsolete use-instead definitions are compared.
        """
        pc = cmp(self.simplified, other.simplified)
        if pc is 0:
            if self.is_registered != other.is_registered:
                # registered < unregistered
                pc = -1 if self.is_registered else 1
            elif self.platform != other.platform:
                # generic < platform
                pc = 1 if self.platform else -1
            elif self.is_complete != other.is_complete:
                # complete < incomplete
                pc = -1 if self.is_complete else 1
            elif self.is_obsolete != other.is_obsolete:
                # current < obsolete
                pc = 1 if self.is_obsolete else -1
            if pc is 0 and self.is_obsolete and (self.use_instead != other.use_instead):
                if self.use_instead is None:
                    pc = -1
                elif other.use_instead is None:
                    pc = 1
                else:
                    pc = cmp(self.use_instead, other.use_instead)
        return pc

    @property
    def extensions(self):
        return self._extensions

    @extensions.setter
    def extensions(self, value):
        self._extensions = [] if value is None else flatten(value)

    @property
    def default_encoding(self):
        return self.media_type == 'text' and 'quoted-printable' or 'base64'

    @property
    def use_instead(self):
        if not self.is_obsolete:
            return None
        return self._use_instead

    @property
    def is_registered(self):
        if UNREG_RE.match(self.raw_media_type) or UNREG_RE.match(self.raw_sub_type):
            return False
        return self.registered

    @property
    def docs(self):
        return self._docs

    @docs.setter
    def docs(self, d):
        if d:
            rs = re.compile('use-instead:([-\w.+]+)\/([-\w.+]*)').findall(d)
            if rs:
                self._use_instead = map(lambda e: "%s/%s" % e, rs)
            else:
                self._use_instead = None
        self._docs = d

    @property
    def urls(self):
        """
        The decoded URL list for this MIME::Type.
        The special URL value IANA will be translated into:
          http://www.iana.org/assignments/media-types/<mediatype>/<subtype>
        The special URL value RFC### will be translated into:
          http://www.rfc-editor.org/rfc/rfc###.txt
        The special URL value DRAFT:name will be
        translated into:
          https://datatracker.ietf.org/public/idindex.cgi?
              command=id_detail&filename=<name>
        The special URL value
        LTSW will be translated
        into:
          http://www.ltsw.se/knbase/internet/<mediatype>.htp
        The special
        URL value
        [token] will
        be translated
        into:
          http://www.iana.org/assignments/contact-people.htm#<token>
        These values will be accessible through #urls, which always returns an array.
        """
        def _url(el):
            if el == 'IANA':
                return IANA_URL % (self.media_type, self.sub_type)
            elif el == 'LTSW':
                return LTSW_URL % self.media_type
            match = re.compile('^\{([^=]+)=([^\}]+)\}').match(el)
            if match:
                return match.group(1, 2)
            match = re.compile('^\[([^=]+)=([^\]]+)\]').match(el)
            if match:
                return [match.group(1), CONTACT_URL % match.group(2)]
            for regex in REGEX_URLS:
                match = re.compile(regex).match(el)
                if match:
                    return REGEX_URLS[regex] % match.group(1)
            return el
        return map(_url, self.url)

    @property
    def encoding(self):
        enc = self._encoding
        if enc is None or enc == 'default':
            return self.default_encoding
        return self._encoding

    @encoding.setter
    def encoding(self, enc):
        if isinstance(enc, basestring) and enc.startswith(':'):
            enc = enc.replace(':', '')

        if enc is None or enc == 'default':
            self._encoding = self.default_encoding
        elif ENCODING_RE.match(enc):
            self._encoding = enc
        else:
            raise TypeError('The encoding must be None, default, '
                            'base64, 7bit, 8bit, or quoted-printable.')

    @property
    def system(self):
        return self._system

    @system.setter
    def system(self, os):
        if os is None or hasattr(os, 'match'):
            self._system = os
        else:
            self._system = re.compile(os)

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
        return not self.is_binary

    @property
    def is_signature(self):
        # Returns +true+ when the simplified MIME type is in the list of
        # known digital signatures.
        return self.simplified.lower() in SIGNATURES

    @property
    def is_system(self):
        # Returns +true+ if the MIME::Type is specific to an operating system.
        return self.system is not None

    @property
    def is_platform(self):
        # Returns +true+ if the MIME::Type is specific to the current operating
        # system as represented by RUBY_PLATFORM.
        return self.is_system and self.system.match(PLATFORM)

    @property
    def is_complete(self):
        # Returns +true+ if the MIME::Type specifies an extension list,
        # indicating that it is a complete MIME::Type.
        return bool(self.extensions)

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
        return [self.content_type, self.extensions, self.encoding, self.system,
                self.is_obsolete, self.docs, self.url, self.is_registered]

    @property
    def to_hash(self):
        # Returns the MIME type as an array suitable for use with
        # MIME::Type.from_hash.
        return {'Content-Type': self.content_type,
                'Content-Transfer-Encoding': self.encoding,
                'Extensions': self.extensions,
                'System': self.system,
                'Obsolete': self.is_obsolete,
                'Docs': self.docs,
                'URL': self.url,
                'Registered': self.is_registered}

    @classmethod
    def simplify(cls, content_type):
        """
        The MIME types main- and sub-label can both start with <tt>x-</tt>,
        which indicates that it is a non-registered name. Of course, after
        registration this flag can disappear, adds to the confusing
        proliferation of MIME types. The simplified string has the
        <tt>x-</tt> removed and are translated to lowercase.
        """
        matchdata = MEDIA_TYPE_RE.match(content_type)
        if matchdata is None:
            return None
        wrap = lambda s: re.sub(UNREG_RE, '', s.lower())
        (media_type, subtype) = matchdata.groups()
        return '%s/%s' % (wrap(media_type), wrap(subtype))

    @classmethod
    def from_array(cls, content_type,
                   extensions=[], encoding=None, system=None,
                   is_obsolete=False, docs=None, url=None, is_registered=False):
        """
        Creates a MIME::Type from an array in the form of:
          [type-name, [extensions], encoding, system]
        +extensions+, +encoding+, and +system+ are optional.
          Type.from_array("application/x-ruby", ['rb'], '8bit')
          # Type.from_array(["application/x-ruby", ['rb'], '8bit'])
        These are equivalent to:
          type = Type('application/x-ruby')
          type.extensions = ['rb']
          type.encoding = '8bit'
        """
        mt = cls(content_type)
        mt.extensions = extensions
        mt.encoding = encoding
        mt.system = system
        mt.is_obsolete = is_obsolete
        mt.docs = docs
        mt.url = url
        mt.registered = is_registered
        return mt

    @classmethod
    def from_hash(cls, hash):
        """
        Creates a MIME::Type from a hash. Keys are case-insensitive,
        dashes may be replaced with underscores, and the internal
        Symbol of the lowercase-underscore version can be used as
        well. That is, Content-Type can be provided as content-type,
        Content_Type, content_type, or :content_type.
        Known keys are <tt>Content-Type</tt>,
        <tt>Content-Transfer-Encoding</tt>, <tt>Extensions</tt>, and
        <tt>System</tt>.
          Type.from_hash({'Content-Type': 'text/x-yaml',
                          'Content-Transfer-Encoding': '8bit',
                          'System': 'linux',
                          'Extensions': ['yaml', 'yml']})
        This is equivalent to:
          t = Type.new('text/x-yaml')
          t.encoding = '8bit'
          t.system = 'linux'
          t.extensions = ['yaml', 'yml']
        """
        wrap_key = lambda k: k.lower().replace('-', '_')
        type_hash = dict([(wrap_key(k), v) for k, v in hash.items()])
        mt = cls(type_hash['content_type'])
        mt.extensions = type_hash.get('extensions', [])
        mt.encoding = type_hash.get('encoding', 'default')
        mt.system = type_hash.get('system')
        mt.is_obsolete = type_hash.get('is_obsolete', False)
        mt.docs = type_hash.get('docs')
        mt.url = type_hash.get('url')
        mt.registered = type_hash.get('is_registered', False)
        return mt

    @classmethod
    def from_mime_type(cls, mime_type):
        """
        Essentially a copy constructor.
         Type.from_mime_type(plaintext)
        is equivalent to:
          t = Type.new(plaintext.content_type.dup)
          t.extensions  = plaintext.extensions.dup
          t.system      = plaintext.system.dup
          t.encoding = plaintext.encoding.dup
        """
        mt = cls(deepcopy(mime_type.content_type))
        mt.extensions = map(deepcopy, mime_type.extensions)
        mt.url = mime_type.url and map(deepcopy, mime_type.url) or None
        mt.system = deepcopy(mime_type.system)
        mt.encoding = deepcopy(mime_type.encoding)
        mt.docs = deepcopy(mime_type.docs)

        mt.is_obsolete = mime_type.is_obsolete
        mt.registered = mime_type.is_registered
        return mt


class ItemMeta(type):
    def __getitem__(cls, type_id):
        if isinstance(type_id, Type):
            return cls.type_variants.get(type_id.simplified)
        elif isinstance(type_id, re._pattern_type):
            return cls.match(type_id)
        else:
            return cls.type_variants.get(Type.simplify(type_id))


class Types(with_metaclass(ItemMeta, object)):
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
    See Also:
        http://www.iana.org/assignments/media-types/
        http://www.ltsw.se/knbase/internet/mime.htp
    """

    type_variants = defaultdict(list)
    extension_index = defaultdict(list)

    __metaclass__ = ItemMeta

    def __init__(self, data_version=None):
        self.data_version = data_version

    def __repr__(self):
        return '<MIME::Types version:%s>' % self.data_version

    @classmethod
    def m(cls, type_id, flags={}):
        return cls.prune_matches(cls[type_id], flags)

    @classmethod
    def match(cls, regex):
        return flatten([v for k, v in iteritems(cls.type_variants)
                        if regex.search(k)])

    @classmethod
    def prune_matches(cls, matches, flags):
        if flags.get('complete'):
            matches = filter(lambda e: e.is_complete, matches)
        if flags.get('platform'):
            matches = filter(lambda e: e.is_platform, matches)
        return list(matches)

    @classmethod
    def add_type_variant(cls, mime_type):
        cls.type_variants[mime_type.simplified].append(mime_type)

    @classmethod
    def index_extensions(cls, mime_type):
        for ext in mime_type.extensions:
            cls.extension_index[ext].append(mime_type)

    @classmethod
    def any(cls, block):
        for mt in flatten(list(itervalues(cls.extension_index))):
            if block(mt):
                return True

    @classmethod
    def all(cls, block):
        return all([block(mt) for mt in flatten(cls.extension_index.values())])

    @classmethod
    def defined_types(cls):
        return chain(*cls.type_variants.values())

    @classmethod
    def count(cls):
        return len(list(cls.defined_types()))

    @classmethod
    def each(cls, block):
        return map(block, cls.defined_types())

    @classmethod
    def type_for(cls, filename, platform=False):
        ext = filename.split('.')[-1].lower()
        type_list = cls.extension_index.get(ext, [])
        if platform:
            type_list = filter(lambda t: t.is_platform, type_list)
        return list(type_list)

    of = type_for

    @classmethod
    def add(cls, *types):
        for mime_type in types:
            if isinstance(mime_type, Types):
                cls.add(*mime_type.defined_types())
            else:
                mts = cls.type_variants.get(mime_type.simplified)
                if mts and mime_type in mts:
                    Warning('Type %s already registered as a variant of %s.',
                            mime_type, mime_type.simplified)
                cls.add_type_variant(mime_type)
                cls.index_extensions(mime_type)
