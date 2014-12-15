#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images from two AVT Manta cameras with the Vimba SDK
#


#
# External dependencies
#
from ctypes import *
import cmd
import os


#
# Image parameters from the camera
#
width = 2452
height = 2056
payloadsize = 5041312


#
# Vimba frame structure
#
class VmbFrame( Structure ) :
	
	_fields_ = [('buffer', c_void_p),
				('bufferSize', c_uint32),
				('context', c_void_p * 4),
				('receiveStatus', c_int32),
				('receiveFlags', c_uint32),
				('imageSize', c_uint32),
				('ancillarySize', c_uint32),
				('pixelFormat', c_uint32),
				('width', c_uint32),
				('height', c_uint32),
				('offsetX', c_uint32),
				('offsetY', c_uint32),
				('frameID', c_uint64),
				('timestamp', c_uint64)]
	
	def __init__( self ) :

		self.ImageBuffer = create_string_buffer( payloadsize )
		self.ImageBufferSize = c_ulong( payloadsize )
		self.AncillaryBuffer = create_string_buffer(0)
		self.AncillaryBufferSize = 0


#
# Main
#
if __name__ == "__main__" :
	

	#
	# Vimba initialization
	#
	print( 'Vimba initialization... ' )

	# Vimba handle constant to access Vimba system features
	vimba_handle = c_void_p(1)

	# Get Vimba installation directory
	vimba_path = "/" + "/".join(os.environ.get("GENICAM_GENTL64_PATH").split("/")[1:-3]) + "/VimbaC/DynamicLib/x86_64bit/libVimbaC.so"
	
	# Load Vimba library
	vimba = cdll.LoadLibrary( vimba_path )
	
	# Initialize the library
	vimba.VmbStartup()
		
	# Set the waiting duration for discovery packets to return
	vimba.VmbFeatureIntSet( vimba_handle, "GeVDiscoveryAllDuration", 250 )
		
	# Send discovery packets to GigE cameras
	vimba.VmbFeatureCommandRun( vimba_handle, "GeVDiscoveryAllOnce" )
	

	#
	# Camera connection
	#
	print( 'Camera connection... ' )
	
	# Initialize camera handles
	camera_1_handle = c_void_p()
	camera_2_handle = c_void_p()
	
	# Connect the cameras
	vimba.VmbCameraOpen( '10.129.11.231', 1, byref(camera_1_handle) )
	vimba.VmbCameraOpen( '10.129.11.232', 1, byref(camera_2_handle) )
		
	
	#
	# Image acquisition
	#
	print( 'Image acquisition... ' )
	
	# Start capture
	vimba.VmbCaptureStart( camera_1_handle )
	vimba.VmbCaptureStart( camera_2_handle )

	# Prepare the frames
	frame_1 = VmbFrame()
	frame_2 = VmbFrame()
	
	# Announce the frames
	print( vimba.VmbFrameAnnounce( camera_1_handle, byref(frame_1), sizeof(frame_1) ) )
	print( vimba.VmbFrameAnnounce( camera_2_handle, byref(frame_2), sizeof(frame_2) ) )

	# End capture
	vimba.VmbCaptureEnd( camera_1_handle )
	vimba.VmbCaptureEnd( camera_2_handle )


	#
	# Camera disconnection
	#
	print( 'Camera disconnection... ' )
	
	# Close the cameras
	vimba.VmbCameraClose( camera_1_handle )
	vimba.VmbCameraClose( camera_2_handle )


	#
	# Vimba shutdown
	#
	print( 'Shutdown Vimba... ' )
	
	# Release the library
	vimba.VmbShutdown()
