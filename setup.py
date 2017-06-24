#/usr/bin/env python
# coding: utf8
from setuptools import setup, find_packages
from bitcron import version

setup(
    name='bitcron',
    version=version,
    description='Command Line Interface for Bitcron',
    author='Hepochen',
    author_email='hepochen@gmail.com',
    url='https://bitcron.com',
    include_package_data=True,
    packages=find_packages(),

    install_requires = [
        'requests >= 2.10.0',
        'Send2Trash >= 1.3.0',
        'python-dateutil'
    ],

    entry_points={
        'console_scripts':[
            'bitcron = bitcron.console:main',
            'farbox = bitcron.console:main'
        ]
    },

    platforms = 'any',

)