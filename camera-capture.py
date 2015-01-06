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
camera = Vimba.VmbCamera( sys.argv[1] )

# Start image acquisition
Viewer.LiveDisplay( camera )

# Camera disconnection
camera.Disconnect()

# Vimba shutdown
Vimba.VmbShutdown()
