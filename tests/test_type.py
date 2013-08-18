# -*- coding: utf-8 -*-
from unittest import main
from framework import MIMETestBase
from mime import Type


class TestMIMEType(MIMETestBase):

    def setUp(self):
        zip_type = Type('x-appl/x-zip')
        zip_type.extensions = ['zip', 'zp']
        self.zip_type = zip_type

    def test_simplify(self):
        self.assertEqual(Type.simplify('text/plain'), 'text/plain')
        self.assertEqual(Type.simplify('image/jpeg'), 'image/jpeg')
        self.assertEqual(Type.simplify('application/x-msword'), 'application/msword')
        self.assertEqual(Type.simplify('text/vCard'), 'text/vcard')
        self.assertEqual(Type.simplify('application/pkcs7-mime'), 'application/pkcs7-mime')
        self.assertEqual(self.zip_type.simplified, 'appl/zip')
        self.assertEqual(Type.simplify('x-xyz/abc'), 'xyz/abc')


if __name__ == '__main__':
    main()
