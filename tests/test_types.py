# -*- coding: utf-8 -*-
import re
from unittest import main
from framework import MIMETestBase
from mime import Type, Types
from mime.type import PLATFORM


class TestMIMETypes(MIMETestBase):

    def test_class_index_1(self):
        text_plain = Type('text/plain')
        text_plain.encoding = '8bit'
        text_plain.extensions = 'asc txt c cc h hh cpp hpp dat hlp'.split()
        text_plain_vms = Type('text/plain')
        text_plain_vms.encoding = '8bit'
        text_plain_vms.extensions = ['doc']
        text_plain_vms.system = 'vms'

        self.assertEqual(Types['text/plain'], [text_plain, text_plain_vms])

    def test_class_index_2(self):
        re_type = re.compile('bmp$')
        tst_bmp = Types['image/x-bmp'] + Types['image/vnd.wap.wbmp'] + Types['image/x-win-bmp']
        self.assertEqual(sorted(tst_bmp), sorted(Types[re_type]))

        Types['image/bmp'][0].system = PLATFORM

        self.assertEqual([Type.from_array('image/x-bmp', ['bmp'])],
                         Types.m(re_type, {'platform': True}))

    def test_class_index_3(self):
        self.assertEqual(Types.m('text/vnd.fly', {'complete': True}), [])
        self.assertNotEqual(Types.m('text/plain', {'complete': True}), [])

    def _test_class_index_extensions(self):
        'Need to write test_class_index_extensions'

    def test_class_add(self):
        eruby = Type('application/x-eruby')
        eruby.extensions = 'rhtml'
        eruby.encoding = '8bit'
        Types.add(eruby)
        self.assertEqual(Types['application/x-eruby'], [eruby])

    def _test_class_add_type_variant(self):
        'Need to write test_class_add_type_variant'

    def test_class_type_for(self):
        self.assertTrue(sorted(Types.type_for('xml')) == sorted(Types['text/xml'] + Types['application/xml']))
        self.assertEqual(Types.type_for('gif'), Types['image/gif'])
        Types['image/gif'][0].system = PLATFORM
        self.assertEqual(Types.type_for('gif', True), Types['image/gif'])
        self.assertEqual(Types.type_for('zzz'), [])

    def test_class_of(self):
        self.assertTrue(sorted(Types.of('xml')) == sorted(Types['text/xml'] + Types['application/xml']))
        self.assertEqual(Types.of('gif'), Types['image/gif'])
        Types['image/gif'][0].system = PLATFORM
        self.assertEqual(Types.of('gif', True), Types['image/gif'])
        self.assertEqual(Types.of('zzz'), [])

    def test_class_enumerable(self):
        self.assertTrue(Types.any(lambda t: t.content_type == 'text/plain'))

    def test_class_count(self):
        self.assertTrue(Types.count() > 42,
                        "A lot of types are expected to be known.")

    def test_ebook_formats(self):
        self.assertEqual(Types['application/x-mobipocket-ebook'], Types.type_for('book.mobi'))
        self.assertEqual(Types['application/epub+zip'], Types.type_for('book.epub'))
        self.assertEqual(Types['application/x-ibooks+zip'], Types.type_for('book.ibooks'))

    def test_apple_formats(self):
        self.assertEqual(Types['application/x-apple-diskimage'],
                         Types.type_for('disk.dmg'))

    def _test_add(self):
        'Need to write test_add'

    def _test_add_type_variant(self):
        'Need to write test_add_type_variant'

    def _test_data_version(self):
        'Need to write test_data_version'

    def _test_index(self):
        'Need to write test_index'

    def _test_index_extensions(self):
        'Need to write test_index_extensions'

    def _test_of(self):
        'Need to write test_of'


if __name__ == '__main__':
    main()
