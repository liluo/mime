# -*- coding: utf-8 -*-
from .type import Type
from .types import Types
from .mime_types import MIMETypes

"""
The namespace for MIME applications, tools, and libraries.
  Reflects a MIME Content-Type which is in invalid format (e.g., it isn't
  in the form of type/subtype).

  The definition of one MIME content-type.

  == Usage
   from mime import Type, Types

   plaintext = Types['text/plain'].first
   # returns [text/plain, text/plain]
   text = plaintext[0]
   print text.media_type            # => 'text'
   print text.sub_type              # => 'plain'
   print " ".join(text.extensions)  # => 'asc txt c cc h hh cpp'
   print text.encoding              # => 8bit
   print text.binary?               # => False
   print text.ascii?                # => True
   print text == 'text/plain'       # => True
   print Type.simplify('x-appl/x-zip') # => 'appl/zip'

   print Types.any(lambda type: type.content_type == 'text/plain')
   # => True
   print Types.all(lambda type: type.is_registered) # => False
"""

VERSION = __version__ = '0.0.1'
