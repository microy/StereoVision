#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images synchronously
# from two AVT Manta cameras with the Vimba SDK
#


#
# External dependencies
#
import Vimba, Viewer


#
# One camera
#
def Live() :

	# Camera connection
	camera = Vimba.VmbCamera( '50-0503323406' )

	# Start image acquisition
	Viewer.LiveDisplay( camera )

	# Camera disconnection
	camera.Disconnect()


#
# Two cameras multithreaded
#
def LiveDual() :

	# Camera connection
	camera_1 = Vimba.VmbCamera( '50-0503323406' )
	camera_2 = Vimba.VmbCamera( '50-0503326223' )

	# Start image acquisition
	Viewer.LiveDisplayDual( camera_1, camera_2 )

	# Close the cameras
	camera_1.Disconnect()
	camera_2.Disconnect()


#
# Stereo cameras (synchronous)
#
def LiveStereo() :

	# Camera connection
	camera_1 = Vimba.VmbCamera( '50-0503323406' )
	camera_2 = Vimba.VmbCamera( '50-0503326223' )

	# Start image acquisition
	Viewer.LiveDisplayStereo( camera_1, camera_2 )

	# Close the cameras
	camera_1.Disconnect()
	camera_2.Disconnect()


#
# Vimba initialization
#
Vimba.VmbStartup()


#
# Start acquisition
#
Live()
#LiveDual()
#LiveStereo()


#
# Vimba shutdown
#
Vimba.VmbShutdown()
