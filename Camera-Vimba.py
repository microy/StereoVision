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
# Vimba handle constant to access Vimba system features
#
VmbHandle = ctypes.c_void_p(1)


#
# Vimba version information structure
#
class VmbVersionInfo( ctypes.Structure ) :
	
	_fields_ = [('major', ctypes.c_uint32),
				('minor', ctypes.c_uint32),
				('patch', ctypes.c_uint32)]


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
		
		# Get Vimba installation directory
		vimba_path = "/" + "/".join(os.environ.get("GENICAM_GENTL64_PATH").split("/")[1:-3]) + "/VimbaC/DynamicLib/x86_64bit/libVimbaC.so"
		
		# Load Vimba library
		self.driver = ctypes.cdll.LoadLibrary( vimba_path )
		
		# Initialize the library
		if self.driver.VmbStartup() :
			print( 'Vimba initialisation failed' )
			
		# Test GigE vision transport layer connection
		gige_vtl_present = ctypes.c_bool()
		self.driver.VmbFeatureBoolGet( VmbHandle, "GeVTLIsPresent", ctypes.byref(gige_vtl_present) )
		if not gige_vtl_present :
			print( 'Could not find the presence of a GigE transport layer' )
			
		# Set the waiting duration for discovery packets to return
		if self.driver.VmbFeatureIntSet( VmbHandle, "GeVDiscoveryAllDuration", 250 ) :
			print( 'Could not set the discovery waiting duration' )
			
		# Send discovery packets to GigE cameras
		if self.driver.VmbFeatureCommandRun( VmbHandle, "GeVDiscoveryAllOnce" ) :
			print( 'Could not ping GigE cameras over the network' )
		
	
	#
	# Post main loop event
	#
	def postloop( self ) :

		# Release the library
		self.driver.VmbShutdown()


	#
	# Print Vimba version number
	#
	def do_version( self, line ) :
		
		version_info = VmbVersionInfo()
		self.driver.VmbVersionQuery( ctypes.byref(version_info), ctypes.sizeof(version_info) )
		print( 'Vimba version {}.{}.{}'.format( version_info.major, version_info.minor, version_info.patch ) )
	
	#
	#
	#
	def do_cameranumber( self, line ) :
		
		camera_number = ctypes.c_uint32()
		self.driver.VmbCamerasList( None, 0, ctypes.byref(camera_number), 0 )
		print( 'Camera found : {}'.format( camera_number.value ) )
	
	
	#
	# Connect a camera via its ID
	#
	def do_connect( self, camera_id ) :
		
		self.camera_handle = ctypes.c_void_p()
		if self.driver.VmbCameraOpen( camera_id, 1, ctypes.byref(self.camera_handle) ) :
			print( 'Camera connection failed' )

		
	#
	# Disconnect the camera
	#
	def do_disconnect( self, line ) :
		
		if self.driver.VmbCameraClose( self.camera_handle ) :
			print( 'Camera disconnection failed' )


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

	
