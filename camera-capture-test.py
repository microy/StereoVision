#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images synchronously
# from two AVT Manta cameras with the Vimba SDK
#


# External dependencies
import Vimba

# Vimba initialization
vimba = Vimba.VmbSystem()
vimba.Startup()

# Camera connection
camera = Vimba.VmbCamera( vimba )
camera.Connect( '50-0503323406' )

# Start image acquisition
camera.LiveDisplay()

# Camera disconnection
camera.Disconnect()

# Vimba shutdown
vimba.Shutdown()
