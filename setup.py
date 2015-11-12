#! /usr/bin/env python
# -*- coding:utf-8 -*-

#
# Setup for the VisionToolkit package
#

# Setup module
from setuptools import setup

# Setup configuration
setup(

    name = 'VisionToolkit',
    version = '0.4dev',
    packages = ['VisionToolkit'],
    scripts = ['StereoVision', 'show_usbcamera.py', 'show_vmbcamera.py'],
    author = 'Michaël Roy',
    author_email = 'microygh@gmail.com',
    description = 'Python Computer Vision Toolkit',
    license = 'MIT',
    url = 'https://github.com/microy/VisionToolkit'

)
