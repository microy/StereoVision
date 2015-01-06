#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images synchronously
# from one AVT camera using the Vimba SDK
#


# External dependencies
import sys
import Vimba, Viewer

# Vimba initialization
Vimba.VmbStartup()

# Camera connection
camera_1 = Vimba.VmbCamera( sys.argv[1] )
camera_2 = Vimba.VmbCamera( sys.argv[2] )

# Start image acquisition
Viewer.LiveDisplayStereo( camera_1, camera_2 )

# Close the cameras
camera_1.Disconnect()
camera_2.Disconnect()

# Camera disconnection
camera.Disconnect()

# Vimba shutdown
Vimba.VmbShutdown()
