#! /usr/bin/env python
# -*- coding:utf-8 -*-

#
# Setup for the StereoVision package
#

# Setup module
from setuptools import setup

# Setup configuration
setup(

    name = 'StereoVision',
    version = '0.4dev',
    packages = ['StereoVision'],
    scripts = ['stereovision.py'],
    author = 'Michaël Roy',
    author_email = 'microygh@gmail.com',
    description = 'Python Stereo Vision Application',
    license = 'MIT',
    url = 'https://github.com/microy/StereoVision'

)
