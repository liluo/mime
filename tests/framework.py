# -*- coding: utf-8 -*-

import os
import sys
from unittest import TestCase

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(TEST_DIR)
LIBS_DIR = os.path.join(ROOT_DIR, "mime")
sys.path.insert(0, LIBS_DIR)


class MIMETestBase(TestCase):
    def setUp(self):
        pass
