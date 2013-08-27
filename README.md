MIME
====
[![Build Status](https://travis-ci.org/liluo/mime.png)](https://travis-ci.org/liluo/mime)

MIME Types for Python, clone of [halostatue/mime-types](https://github.com/halostatue/mime-types).

This library allows for the identification of a file's likely MIME content type. 

MIME types are used in MIME-compliant communications, as in e-mail or HTTP
traffic, to indicate the type of content which is transmitted. MIME Types
provides the ability for detailed information about MIME entities (provided as
a set of MIME Type objects) to be determined and used programmatically. There
are many types defined by RFCs and vendors, so the list is long but not
complete; don't hesitate to ask to add additional information. This library
follows the IANA collection of MIME types (see below for reference).

MIME Types is built to conform to the MIME types of RFCs 2045 and 2231. It
tracks the [IANA registry](http://www.iana.org/assignments/media-types/)
([ftp](ftp://ftp.iana.org/assignments/media-types)) with some unofficial types
added from the [LTSW collection](http://www.ltsw.se/knbase/internet/mime.htp)
and added by the users of MIME Types.

### Installation

```bash
pip install mime
```

or

```bash
easy_install mime
```

### Features

MIME types are used in MIME entities, as in email or HTTP traffic. 
It is useful at times to have information available about MIME types (or, inversely, about files). 
A MIME Type stores the known information about one MIME type.

```bash
import mime

plaintext = mime.Types['text/plain']
# => [<MIME::Type text/plain>, <MIME::Type text/plain>]
text = plaintext[0]

print text.media_type             # => 'text'
print text.sub_type               # => 'plain'
print ' '.join(text.extensions)   # => 'txt asc c cc h hh cpp hpp dat hlp'

print text.encoding               # => 'quoted-printable'
print text.is_binary              # => False
print text.is_ascii               # => True
print text.is_obsolete            # => False
print text.is_registered          # => True
print str(text) == 'text/plain'   # => True
print mime.Type.simplify('x-appl/x-zip')  # => 'appl/zip'

print mime.Types.any(lambda t: t.content_type == 'text/plain')  # => True
print mime.Types.all(lambda t: t.is_registered)                 # => False

py = mime.Types.of('script.py')[0]
print py.content_type             # => 'application/x-python'
print py.encoding                 # => '8bit'
print py.is_binary                # => False
print py.simplified               # => 'application/python'

rb_types = mime.Types.of('script.rb')
rb = rb_types[0]
print rb.content_type             # => 'application/x-ruby'
print rb.is_ascii                 # => True
print rb.extensions               # => ['rb', 'rbw']

import re
image_types = mime.Types[re.compile('image')]
# => [<MIME::Type image/vnd.microsoft.icon>, <MIME::Type application/x-imagemap>, ...] 
print mime.Types.count()          # => 1643
```

### Contributing

```bash
* Fork the repository.
* Create a topic branch.
* Implement your feature or bug fix.
* Add, commit, and push your changes.
* Submit a pull request.
```

#### Testing

```bash
cd tests/
python run.py
```

### Changelog
__v0.0.2 [2013-08-27]__
* It's worked.

__v0.0.1 [2013-08-13]__
* Register name.
