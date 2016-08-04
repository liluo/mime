#!/usr/bin/env python
import os
import re

from setuptools import setup, find_packages

with open('mime/version.py', 'r') as fd:
    version = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
        raise RuntimeError('Cannot find version information')

setup(name='mime',
      version=version,
      keywords='mime types',
      description='MIME Types',
      long_description=open(os.path.join(os.path.dirname(__file__),
                                         'README.md')).read(),

      license='MIT License',
      url='https://github.com/liluo/mime',
      author='liluo',
      author_email='i@liluo.org',

      packages=find_packages(),
      include_package_data=True,
      platforms=['POSIX'],
      classifiers=['Programming Language :: Python',
                   'Operating System :: POSIX'],
      install_requires=['future'])
