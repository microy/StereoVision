# -*- coding:utf-8 -*-


#
# Interface to the AVT Vimba SDK
#


#
# Inspired from :
#
#       - Pymba
#         https://github.com/morefigs/pymba
#


#
# External dependencies
#
import os
import time
import threading
import ctypes as ct
import numpy as np


#
# Global access to the Vimba library
#
vimba = None


#
# Initialize the Vimba library
#
def VmbStartup() :

	# Get Vimba installation directory
	vimba_path = '/' + '/'.join( os.environ.get( 'GENICAM_GENTL64_PATH' ).split( '/' )[ 1 : -3 ] )
	vimba_path += '/VimbaC/DynamicLib/x86_64bit/libVimbaC.so'

	# Load Vimba library
	global vimba
	vimba = ct.cdll.LoadLibrary( vimba_path )

	# Initialize the library
	vimba.VmbStartup()

	# Send discovery packet to GigE cameras
	vimba.VmbFeatureCommandRun( ct.c_void_p(1), 'GeVDiscoveryAllOnce' )


#
# Release the Vimba library
#
def VmbShutdown() :

	# Release the library
	vimba.VmbShutdown()


#
# Vimba frame structure
#
class VmbFrame( ct.Structure ) :

	#
	# VmbFrame structure fields
	#
	_fields_ = [ ( 'buffer', ct.POINTER( ct.c_char ) ),
			( 'bufferSize', ct.c_uint32 ),
			( 'context', ct.c_void_p * 4 ),
			( 'receiveStatus', ct.c_int32 ),
			( 'receiveFlags', ct.c_uint32 ),
			( 'imageSize', ct.c_uint32 ),
			( 'ancillarySize', ct.c_uint32 ),
			( 'pixelFormat', ct.c_uint32 ),
			( 'width', ct.c_uint32 ),
			( 'height', ct.c_uint32 ),
			( 'offsetX', ct.c_uint32 ),
			( 'offsetY', ct.c_uint32 ),
			( 'frameID', ct.c_uint64 ),
			( 'timestamp', ct.c_uint64 ) ]

	#
	# Initialize the image buffer
	#
	def __init__( self, frame_size ) :

		self.buffer = ct.create_string_buffer( frame_size )
		self.bufferSize = ct.c_uint32( frame_size )

	#
	# Convert the frame to a numpy array
	#
	@property
	def image( self ) :

		return np.ndarray( buffer=self.buffer[ 0 : self.bufferSize ], dtype=np.uint8, shape=( self.height, self.width ) )


#
# Vimba camera
#
class VmbCamera( object ) :

	#
	# Initialize the camera
	#
	def __init__( self, camera_id ) :

		# Camera handle
		self.handle = ct.c_void_p()

		# Camera ID (serial number, IP address...)
		self.id = camera_id

	#
	# Open the camera
	#
	def Open( self ) :

		# Connect the camera
		vimba.VmbCameraOpen( self.id, 1, ct.byref( self.handle ) )

		# Adjust packet size automatically
		vimba.VmbFeatureCommandRun( self.handle, 'GVSPAdjustPacketSize' )

		# Query image parameters
		tmp_value = ct.c_int()
		vimba.VmbFeatureIntGet( self.handle, 'Width', ct.byref( tmp_value ) )
		self.width = tmp_value.value
		vimba.VmbFeatureIntGet( self.handle, 'Height', ct.byref( tmp_value ) )
		self.height = tmp_value.value
		vimba.VmbFeatureIntGet( self.handle, 'PayloadSize', ct.byref( tmp_value ) )
		self.payloadsize = tmp_value.value

	#
	# Close the camera
	#
	def Close( self ) :

		# Close the camera
		vimba.VmbCameraClose( self.handle )

	#
	# Start the acquisition
	#
	def StartCapture( self, image_callback, frame_buffer_size = 10 ) :

		# Register the external image callback function
		self.image_callback = image_callback

		# Register the internal frame callback function
		self.frame_callback = ct.CFUNCTYPE( None, ct.c_void_p, ct.POINTER(VmbFrame) )( self.FrameCallback )

		# Initialize frame buffer
		self.frame_buffer = []
		for i in range( frame_buffer_size ) :
			self.frame_buffer.append( VmbFrame( self.payloadsize ) )

		# Announce the frames
		for i in range( frame_buffer_size ) :
			vimba.VmbFrameAnnounce( self.handle, ct.byref(self.frame_buffer[i]), ct.sizeof(self.frame_buffer[i]) )

		# Start capture engine
		vimba.VmbCaptureStart( self.handle )

		# Queue the frames
		for i in range( frame_buffer_size ) :
			vimba.VmbCaptureFrameQueue( self.handle, ct.byref(self.frame_buffer[i]), self.frame_callback )

		# Start acquisition
		vimba.VmbFeatureCommandRun( self.handle, 'AcquisitionStart' )

	#
	# Stop the acquisition
	#
	def StopCapture( self ) :

		# Stop acquisition
		vimba.VmbFeatureCommandRun( self.handle, 'AcquisitionStop' )

		# Flush the frame queue
		vimba.VmbCaptureQueueFlush( self.handle )

		# Stop capture engine
		vimba.VmbCaptureEnd( self.handle )

		# Revoke frames
		vimba.VmbFrameRevokeAll( self.handle )

	#
	# Frame callback function called by Vimba
	#
	def FrameCallback( self, camera, frame ) :

		# Check frame validity
		if not frame.contents.receiveStatus :

			# Call external image callback function
			self.image_callback( frame.contents.image )

		# Requeue the frame so it can be filled again
		vimba.VmbCaptureFrameQueue( camera, frame, self.frame_callback )


#
# Vimba stereo camera
#
class VmbStereoCamera( object ) :

	#
	# Initialize the cameras
	#
	def __init__( self, camera_left_id, camera_right_id ) :

		# Camera connection
		self.camera_left = VmbCamera( camera_left_id )
		self.camera_right = VmbCamera( camera_right_id )

	#
	# Open the cameras
	#
	def Open( self ) :

		# Open the cameras
		self.camera_left.Open()
		self.camera_right.Open()

	#
	# Close the cameras
	#
	def Close( self ) :

		# Close the cameras
		self.camera_left.Close()
		self.camera_right.Close()

	#
	# Start synchronous acquisition
	#
	def StartCapture( self, image_callback ) :

		# Register the external image callback function
		self.image_callback = image_callback

		# Initialize frame status
		self.image_left_ready = False
		self.image_right_ready = False

		# Start acquisition
		self.camera_left.StartCapture( self.ImageCallbackLeft )
		self.camera_right.StartCapture( self.ImageCallbackRight )

	#
	# Stop the acquisition
	#
	def StopCapture( self ) :

		# Stop image acquisition
		self.camera_left.StopCapture()
		self.camera_right.StopCapture()

	#
	# Receive a frame from camera left
	#
	def ImageCallbackLeft( self, image ) :

		# Save the current frame
		self.image_left = image

		# Frame ready
		self.image_left_ready = True

		# Synchronize the frames
		self.Synchronize()

	#
	# Receive a frame from camera right
	#
	def ImageCallbackRight( self, image ) :

		# Save the current frame
		self.image_right = image

		# Frame ready
		self.image_right_ready = True

		# Synchronize the frames
		self.Synchronize()

	#
	# Synchronize the images from both camera
	#
	def Synchronize( self ) :

		# Wait for both images
		if self.image_left_ready and self.image_right_ready :

			# Send the images to the external program
			self.image_callback( self.image_left, self.image_right )

			# Initialize image status
			self.image_left_ready = False
			self.image_right_ready = False
