#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images asynchronously
# from two AVT Manta cameras with the Vimba SDK
#


#
# External dependencies
#
import cv2
import ctypes as ct
import numpy as np
import Vimba
import Viewer



#
# Main program
#


# Vimba initialization
Vimba.VmbStartup()
vimba = Vimba.vimba

# Camera connection
camera1 = Vimba.VmbCamera( '50-0503323406' )
camera2 = Vimba.VmbCamera( '50-0503326223' )

# Live view of the cameras
viewer = Viewer.StereoViewer( camera1, camera2 )
viewer.LiveDisplay()

# Stop image acquisition
camera1.CaptureStop()
camera2.CaptureStop()

# Cleanup OpenCV
cv2.destroyAllWindows()

# Camera disconnection
camera1.Disconnect()
camera2.Disconnect()

# Vimba shutdown
vimba.VmbShutdown()


