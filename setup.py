#!/usr/bin/env python
import os
from mime import VERSION
from setuptools import setup, find_packages


setup(name='mime',
      version=VERSION,
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
      install_requires=[])
