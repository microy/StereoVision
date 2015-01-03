#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images synchronously
# from two AVT Manta cameras with the Vimba SDK
#


#
# External dependencies
#
import Vimba


#
# One camera
#
def Live() :

	# Camera connection
	camera = Vimba.VmbCamera( '50-0503323406' )

	# Start image acquisition
	camera.LiveDisplay()

	# Camera disconnection
	camera.Disconnect()


#
# Two cameras multithreaded
#
def LiveDual() :

	# Camera connection
	dual_camera = Vimba.VmbDualCamera( '50-0503323406', '50-0503326223' )

	# Start image acquisition
	dual_camera.LiveDisplay()

	# Camera disconnection
	dual_camera.Disconnect()


#
# Stereo cameras (synchronous)
#
def LiveStereo() :

	# Camera connection
	stereo_camera = Vimba.VmbStereoCamera( '50-0503323406', '50-0503326223' )

	# Start image acquisition
	stereo_camera.LiveDisplay()

	# Camera disconnection
	stereo_camera.Disconnect()


#
# Vimba initialization
#
Vimba.VmbStartup()


#
# Start acquisition
#
Live()
LiveDual()
LiveStereo()


#
# Vimba shutdown
#
Vimba.VmbShutdown()
