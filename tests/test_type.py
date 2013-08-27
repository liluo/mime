# -*- coding: utf-8 -*-
import re
from unittest import main
from framework import MIMETestBase
from mime import Type
from mime.type import PLATFORM_RE, InvalidContentType


class TestMIMEType(MIMETestBase):

    def setUp(self):
        zip_type = Type('x-appl/x-zip')
        zip_type.extensions = ['zip', 'zp']
        self.zip_type = zip_type

    @property
    def yaml_mime_type_from_array(self):
        return Type.from_array('text/x-yaml', ['yaml', 'yml'], '8bit', 'd9d172f608')

    def test_class_from_array(self):
        yaml = self.yaml_mime_type_from_array
        self.assertTrue(isinstance(yaml, Type))
        self.assertEqual('text/yaml', yaml.simplified)

    def test_class_from_hash(self):
        yaml = Type.from_hash({'Content-Type': 'text/x-yaml',
                               'Content-Transfer-Encoding': '8bit',
                               'System': 'd9d172f608',
                               'Extensions': ['yaml', 'yml']})
        self.assertTrue(isinstance(yaml, Type))
        self.assertEqual('text/yaml', yaml.simplified)

    def test_class_from_mime_type(self):
        zip2 = Type.from_mime_type(self.zip_type)
        self.assertTrue(isinstance(zip2, Type))
        self.assertEqual('appl/zip', self.zip_type.simplified)
        self.assertNotEqual(id(self.zip_type), id(zip2))

    def test_simplified(self):
        self.assertEqual(Type.simplify('text/plain'), 'text/plain')
        self.assertEqual(Type.simplify('image/jpeg'), 'image/jpeg')
        self.assertEqual(Type.simplify('application/x-msword'), 'application/msword')
        self.assertEqual(Type.simplify('text/vCard'), 'text/vcard')
        self.assertEqual(Type.simplify('application/pkcs7-mime'), 'application/pkcs7-mime')
        self.assertEqual(self.zip_type.simplified, 'appl/zip')
        self.assertEqual(Type.simplify('x-xyz/abc'), 'xyz/abc')

    def test_CMP(self):
        self.assertEqual(Type('text/plain'), Type('text/plain'))
        self.assertNotEqual(Type('text/plain'), Type('image/jpeg'))
        self.assertEqual(Type('text/plain').to_s, 'text/plain')
        self.assertNotEqual(Type('text/plain').to_s, 'image/jpeg')
        self.assertTrue(Type('text/plain') > Type('text/html'))
        self.assertTrue(Type('text/plain') > 'text/html')
        self.assertTrue(Type('text/html') < Type('text/plain'))
        self.assertTrue(Type('text/html') < 'text/plain')
        self.assertEqual('text/html', Type('text/html').to_s)
        self.assertTrue('text/html' < Type('text/plain'))
        self.assertTrue('text/plain' > Type('text/html'))

    def test_ascii_eh(self):
        self.assertTrue(Type('text/plain').is_ascii)
        self.assertFalse(Type('image/jpeg').is_ascii)
        self.assertFalse(Type('application/x-msword').is_ascii)
        self.assertTrue(Type('text/vCard').is_ascii)
        self.assertFalse(Type('application/pkcs7-mime').is_ascii)
        self.assertFalse(self.zip_type.is_ascii)

    def test_binary_eh(self):
        self.assertFalse(Type('text/plain').is_binary)
        self.assertTrue(Type('image/jpeg').is_binary)
        self.assertTrue(Type('application/x-msword').is_binary)
        self.assertFalse(Type('text/vCard').is_binary)
        self.assertTrue(Type('application/pkcs7-mime').is_binary)
        self.assertTrue(self.zip_type.is_binary)

    def test_complete_eh(self):
        yaml = self.yaml_mime_type_from_array
        self.assertTrue(yaml.is_complete)
        yaml.extensions = None
        self.assertFalse(yaml.is_complete)

    def test_content_type(self):
        self.assertEqual(Type('text/plain').content_type, 'text/plain')
        self.assertEqual(Type('image/jpeg').content_type, 'image/jpeg')
        self.assertEqual(Type('application/x-msword').content_type, 'application/x-msword')
        self.assertEqual(Type('text/vCard').content_type, 'text/vCard')
        self.assertEqual(Type('application/pkcs7-mime').content_type, 'application/pkcs7-mime')
        self.assertEqual(self.zip_type.content_type, 'x-appl/x-zip')

    def test_encoding(self):
        self.assertEqual(Type('text/plain').encoding, 'quoted-printable')
        self.assertEqual(Type('image/jpeg').encoding, 'base64')
        self.assertEqual(Type('application/x-msword').encoding, 'base64')
        self.assertEqual(Type('text/vCard').encoding, 'quoted-printable')
        self.assertEqual(Type('application/pkcs7-mime').encoding, 'base64')

        yaml = self.yaml_mime_type_from_array
        self.assertEqual(yaml.encoding, '8bit')
        yaml.encoding = 'base64'
        self.assertEqual(yaml.encoding, 'base64')
        yaml.encoding = 'default'
        self.assertEqual(yaml.encoding, 'quoted-printable')

        def raise_func(yaml):
            yaml.encoding = 'binary'
        self.assertRaises(TypeError, raise_func, yaml)
        self.assertEqual(self.zip_type.encoding, 'base64')

    def _test_default_encoding(self):
        'Need to write test_default_encoding'

    def _test_docs(self):
        'Need to write test_docs'

    def _test_docs_equals(self):
        'Need to write test_docs_equals'

    def _test_encoding_equals(self):
        'Need to write test_encoding_equals'

    def test_eql(self):
        self.assertTrue(Type('text/plain') == Type('text/plain'))
        self.assertFalse(Type('text/plain') == Type('image/jpeg'))
        self.assertFalse(Type('text/plain') == 'text/plain')
        self.assertFalse(Type('text/plain') == 'image/jpeg')

    def test_extensions(self):
        yaml = self.yaml_mime_type_from_array
        self.assertEqual(yaml.extensions, ['yaml', 'yml'])
        yaml.extensions = 'yaml'
        self.assertEqual(yaml.extensions, ['yaml'])
        self.assertEqual(len(self.zip_type.extensions), 2)
        self.assertEqual(self.zip_type.extensions, ['zip', 'zp'])

    def _test_extensions_equals(self):
        'Need to write test_extensions_equals'

    def test_like_eh(self):
        self.assertTrue(Type('text/plain').is_like(Type('text/plain')))
        self.assertTrue(Type('text/plain').is_like(Type('text/x-plain')))
        self.assertFalse(Type('text/plain').is_like(Type('image/jpeg')))
        self.assertTrue(Type('text/plain').is_like('text/plain'))
        self.assertTrue(Type('text/plain').is_like('text/x-plain'))
        self.assertFalse(Type('text/plain').is_like('image/jpeg'))

    def test_media_type(self):
        self.assertEqual(Type('text/plain').media_type, 'text')
        self.assertEqual(Type('image/jpeg').media_type, 'image')
        self.assertEqual(Type('application/x-msword').media_type, 'application')
        self.assertEqual(Type('text/vCard').media_type, 'text')
        self.assertEqual(Type('application/pkcs7-mime').media_type, 'application')
        self.assertEqual(Type('x-chemical/x-pdb').media_type, 'chemical')
        self.assertEqual(self.zip_type.media_type, 'appl')

    def _test_obsolete_eh(self):
        'Need to write test_obsolete_eh'

    def _test_obsolete_equals(self):
        'Need to write test_obsolete_equals'

    def test_platform_eh(self):
        yaml = self.yaml_mime_type_from_array
        self.assertFalse(yaml.is_platform)
        yaml.system = None
        self.assertFalse(yaml.is_platform)
        yaml.system = PLATFORM_RE
        self.assertTrue(yaml.is_platform)

    def test_raw_media_type(self):
        self.assertEqual(Type('text/plain').raw_media_type, 'text')
        self.assertEqual(Type('image/jpeg').raw_media_type, 'image')
        self.assertEqual(Type('application/x-msword').raw_media_type, 'application')
        self.assertEqual(Type('text/vCard').raw_media_type, 'text')
        self.assertEqual(Type('application/pkcs7-mime').raw_media_type, 'application')

        self.assertEqual(Type('x-chemical/x-pdb').raw_media_type, 'x-chemical')
        self.assertEqual(self.zip_type.raw_media_type, 'x-appl')

    def test_raw_sub_type(self):
        self.assertEqual(Type('text/plain').raw_sub_type, 'plain')
        self.assertEqual(Type('image/jpeg').raw_sub_type, 'jpeg')
        self.assertEqual(Type('application/x-msword').raw_sub_type, 'x-msword')
        self.assertEqual(Type('text/vCard').raw_sub_type, 'vCard')
        self.assertEqual(Type('application/pkcs7-mime').raw_sub_type, 'pkcs7-mime')
        self.assertEqual(self.zip_type.raw_sub_type, 'x-zip')

    def test_registered_eh(self):
        self.assertTrue(Type('text/plain').is_registered)
        self.assertTrue(Type('image/jpeg').is_registered)
        self.assertFalse(Type('application/x-msword').is_registered)
        self.assertTrue(Type('text/vCard').is_registered)
        self.assertTrue(Type('application/pkcs7-mime').is_registered)
        self.assertFalse(self.zip_type.is_registered)

    def _test_registered_equals(self):
        'Need to write test_registered_equals'

    def test_signature_eh(self):
        self.assertFalse(Type('text/plain').is_signature)
        self.assertFalse(Type('image/jpeg').is_signature)
        self.assertFalse(Type('application/x-msword').is_signature)
        self.assertTrue(Type('text/vCard').is_signature)
        self.assertTrue(Type('application/pkcs7-mime').is_signature)

    def test_sub_type(self):
        self.assertEqual(Type('text/plain').sub_type, 'plain')
        self.assertEqual(Type('image/jpeg').sub_type, 'jpeg')
        self.assertEqual(Type('application/x-msword').sub_type, 'msword')
        self.assertEqual(Type('text/vCard').sub_type, 'vcard')
        self.assertEqual(Type('application/pkcs7-mime').sub_type, 'pkcs7-mime')
        self.assertEqual(self.zip_type.sub_type, 'zip')

    def test_system_equals(self):
        yaml = self.yaml_mime_type_from_array
        self.assertEqual(yaml.system, re.compile('d9d172f608'))
        yaml.system = 'win32'
        self.assertEqual(yaml.system, re.compile('win32'))
        yaml.system = None
        self.assertTrue(yaml.system is None)

    def test_system_eh(self):
        yaml = self.yaml_mime_type_from_array
        self.assertTrue(yaml.is_system)
        yaml.system = None
        self.assertFalse(yaml.is_system)

    def test_to_a(self):
        yaml = self.yaml_mime_type_from_array
        self.assertEqual(yaml.to_a, ['text/x-yaml', ['yaml', 'yml'], '8bit',
                                     re.compile('d9d172f608'), False, None, None, False])

    def test_to_hash(self):
        yaml = self.yaml_mime_type_from_array
        self.assertEqual(yaml.to_hash, {'Content-Type': 'text/x-yaml',
                                        'Content-Transfer-Encoding': '8bit',
                                        'Extensions': ['yaml', 'yml'],
                                        'System': re.compile('d9d172f608'),
                                        'Registered': False,
                                        'URL': None,
                                        'Obsolete': False,
                                        'Docs': None})

    def test_to_s(self):
        self.assertEqual(Type('text/plain').to_s, 'text/plain')
        self.assertEqual(str(Type('text/plain')), 'text/plain')

    def test_class_constructors(self):
        self.assertTrue(self.zip_type is not None)
        yaml = Type('text/x-yaml')
        yaml.extensions = ['yaml', 'yml']
        yaml.encoding = '8bit'
        yaml.system = 'd9d172f608'
        self.assertTrue(isinstance(yaml, Type))

        def error_content_type(ct):
            return Type(ct)
        self.assertRaises(InvalidContentType, error_content_type, 'apps')
        self.assertRaises(InvalidContentType, error_content_type, None)

    def _test_to_str(self):
        'Need to write test_to_str'

    def _test_url(self):
        'Need to write test_url'

    def _test_url_equals(self):
        'Need to write test_url_equals'

    def _test_urls(self):
        'Need to write test_urls'

    def __test_use_instead(self):
        'Need to write test_use_instead'


if __name__ == '__main__':
    main()
