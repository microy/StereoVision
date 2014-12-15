#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images from two AVT Manta cameras with the Vimba SDK
#


#
# External dependencies
#
import ctypes
import time
import cmd
import socket
import os


#
# Vimba frame structure
#
class VmbFrame( ctypes.Structure ) :
	
	_fields_ = [('buffer', ctypes.c_void_p),
				('bufferSize', ctypes.c_uint32),
				('context', ctypes.c_void_p * 4),
				('receiveStatus', ctypes.c_int32),
				('receiveFlags', ctypes.c_uint32),
				('imageSize', ctypes.c_uint32),
				('ancillarySize', ctypes.c_uint32),
				('pixelFormat', ctypes.c_uint32),
				('width', ctypes.c_uint32),
				('height', ctypes.c_uint32),
				('offsetX', ctypes.c_uint32),
				('offsetY', ctypes.c_uint32),
				('frameID', ctypes.c_uint64),
				('timestamp', ctypes.c_uint64)]


#
# Shell to interface the Vimba library
#
class Shell( cmd.Cmd ) :
	
	
	#
	# Shell customization
	#
	prompt = '> '
	intro = '\n~~ AVT Vimba SDK Interface ~~\n'
	ruler = '-'
	doc_header = ''
	misc_header = ''
	undoc_header = ''


	#
	# Pre main loop event
	#
	def preloop( self ) :
		
		# Vimba handle constant to access Vimba system features
		VmbHandle = ctypes.c_void_p(1)

		# Get Vimba installation directory
		vimba_path = "/" + "/".join(os.environ.get("GENICAM_GENTL64_PATH").split("/")[1:-3]) + "/VimbaC/DynamicLib/x86_64bit/libVimbaC.so"
		
		# Load Vimba library
		self.vimba = ctypes.cdll.LoadLibrary( vimba_path )
		
		# Initialize the library
		if self.vimba.VmbStartup() :
			print( 'Vimba initialisation failed' )
			
		# Test GigE vision transport layer connection
		gige_vtl_present = ctypes.c_bool()
		self.vimba.VmbFeatureBoolGet( VmbHandle, "GeVTLIsPresent", ctypes.byref(gige_vtl_present) )
		if not gige_vtl_present :
			print( 'Could not find the presence of a GigE transport layer' )
			
		# Set the waiting duration for discovery packets to return
		if self.vimba.VmbFeatureIntSet( VmbHandle, "GeVDiscoveryAllDuration", 250 ) :
			print( 'Could not set the discovery waiting duration' )
			
		# Send discovery packets to GigE cameras
		if self.vimba.VmbFeatureCommandRun( VmbHandle, "GeVDiscoveryAllOnce" ) :
			print( 'Could not ping GigE cameras over the network' )
		
	
	#
	# Post main loop event
	#
	def postloop( self ) :

		# Release the library
		self.vimba.VmbShutdown()


	#
	# Connect the two cameras with their IP address
	#
	def do_connect( self, camera_id ) :
		
		self.camera_1_handle = ctypes.c_void_p()
		if self.vimba.VmbCameraOpen( '10.129.11.231', 1, ctypes.byref(self.camera_1_handle) ) :
			print( 'Camera 1 connection failed' )
		self.camera_2_handle = ctypes.c_void_p()
		if self.vimba.VmbCameraOpen( '10.129.11.232', 1, ctypes.byref(self.camera_2_handle) ) :
			print( 'Camera 2 connection failed' )

		
	#
	# Disconnect the camera
	#
	def do_disconnect( self, line ) :
		
		if self.vimba.VmbCameraClose( self.camera_1_handle ) :
			print( 'Camera 1 disconnection failed' )
		if self.vimba.VmbCameraClose( self.camera_2_handle ) :
			print( 'Camera 2 disconnection failed' )


	#
	# Quit gracefully
	#
	def do_exit( self, line ) :
		
		return True

	
	#
	# Handle empty lines
	#
	def emptyline( self ) :
		
         pass


#
# Main
#
if __name__ == "__main__" :
	
	Shell().cmdloop()

	
