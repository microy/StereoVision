#! /usr/bin/env python
# -*- coding:utf-8 -*- 

#
# Setup for the VisionToolkit package
#

# Setup module
from setuptools import setup

# Setup configuration
setup(

    name = "VisionToolkit",
    version = "0.4",
    packages = ['VisionToolkit'],
    scripts = ['StereoVision'],
    author = "Michaël Roy",
    author_email = "microygh@gmail.com",
    description = "Python Computer Vision Toolkit",
    license = "MIT",
    url = "https://github.com/microy/VisionToolkit"
    
)
