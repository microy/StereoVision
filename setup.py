#! /usr/bin/env python
# -*- coding:utf-8 -*- 

#
# Setup for the PyStereoVisionToolkit package
#

# External dependencies
from setuptools import setup, find_packages

# Setup configuration
setup(

    name = "PyStereoVisionToolkit",
    version = "0.1dev",
    packages = find_packages(),
    scripts = ['StereoVision.py'],
    author = "Michaël Roy",
    author_email = "microygh@gmail.com",
    description = "Python StereoVision Toolkit",
    license = "MIT",
    url = "https://github.com/microy/PyStereoVisionToolkit",

)
