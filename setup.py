#! /usr/bin/env python
# -*- coding:utf-8 -*- 

#
# Setup for the PyStereoVisionToolkit package
#

# Setup module
try :
	from setuptools import setup
except ImportError :
	from distutils.core import setup

# Setup configuration
setup(

    name = "PyStereoVisionToolkit",
    version = "0.1",
    packages = ['PyStereoVisionToolkit'],
    scripts = ['StereoVision'],
    author = "Michaël Roy",
    author_email = "microygh@gmail.com",
    description = "Python StereoVision Toolkit",
    license = "MIT",
    url = "https://github.com/microy/PyStereoVisionToolkit"
    
)
