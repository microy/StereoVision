#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images synchronously
# from two AVT Manta cameras with the Vimba SDK
#


# External dependencies
import Vimba


# One camera
def Live( vimba_system ) :

	# Camera connection
	camera = Vimba.VmbCamera( vimba_system )
	camera.Connect( '50-0503323406' )

	# Start image acquisition
	camera.LiveDisplay()

	# Camera disconnection
	camera.Disconnect()


# Two camera
def LiveDual( vimba_system ) :

	# Camera connection
	dual_camera = Vimba.VmbDualCamera( vimba_system )
	dual_camera.Connect( '50-0503323406', '50-0503326223' )

	# Start image acquisition
	dual_camera.LiveDisplay()

	# Camera disconnection
	dual_camera.Disconnect()


# Stereo cameras
def LiveStereo( vimba_system ) :

	# Camera connection
	stereo_camera = Vimba.VmbStereoCamera( vimba_system )
	stereo_camera.Connect( '50-0503323406', '50-0503326223' )

	# Start image acquisition
	stereo_camera.LiveDisplay()

	# Camera disconnection
	stereo_camera.Disconnect()


# Vimba initialization
vimba = Vimba.VmbSystem()
vimba.Startup()

# Start acquisition
#Live( vimba )
#LiveDual( vimba )
LiveStereo( vimba )

# Vimba shutdown
vimba.Shutdown()
