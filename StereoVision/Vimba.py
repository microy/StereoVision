# -*- coding:utf-8 -*-

#
# Interface to the Allied Vision Vimba SDK
#

# Inspired from :
#  - Allied Vision Vimba SDK (https://www.alliedvision.com/en/products/software.html)
#  - Pymba (https://github.com/morefigs/pymba)
#  - ROS (http://wiki.ros.org/avt_vimba_camera)

# External dependencies
import os
import sys
import time
import ctypes as ct
import numpy as np

# The Vimba library
vimba = None

# Initialize the Vimba library
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
	vimba.VmbFeatureCommandRun( ct.c_void_p( 1 ), 'GeVDiscoveryAllOnce' )

# Release the Vimba library
def VmbShutdown() :
	# Release the library
	vimba.VmbShutdown()

# Vimba frame structure
class VmbFrame( ct.Structure ) :
	# VmbFrame structure fields
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
	# Initialize the image buffer
	def __init__( self, frame_size ) :
		self.buffer = ct.create_string_buffer( frame_size )
		self.bufferSize = ct.c_uint32( frame_size )
	# Convert the frame to a numpy array
	@property
	def image( self ) :
		return np.ndarray( buffer = self.buffer[ 0 : self.bufferSize ], dtype = np.uint8, shape = ( self.height, self.width ) )
	# Tell if the frame is valid
	@property
	def is_valid( self ) :
		return not self.receiveStatus

# Vimba camera
class VmbCamera( object ) :
	# Initialize the camera
	def __init__( self, camera_id ) :
		# Camera handle
		self.handle = ct.c_void_p()
		# Camera ID (serial number, IP address...)
		self.id = camera_id
	# Open the camera
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
	# Close the camera
	def Close( self ) :
		vimba.VmbCameraClose( self.handle )
	# Start the acquisition
	def StartCapture( self, frame_callback, frame_buffer_size = 10 ) :
		# Register the external frame callback function
		self.frame_callback = frame_callback
		# Register the internal frame callback function
		self.vmb_frame_callback = ct.CFUNCTYPE( None, ct.c_void_p, ct.POINTER( VmbFrame ) )( self.VmbFrameCallback )
		# Initialize frame buffer
		self.frame_buffer = []
		for i in range( frame_buffer_size ) :
			self.frame_buffer.append( VmbFrame( self.payloadsize ) )
		# Announce the frames
		for i in range( frame_buffer_size ) :
			vimba.VmbFrameAnnounce( self.handle, ct.byref( self.frame_buffer[i] ), ct.sizeof( self.frame_buffer[i] ) )
		# Start capture engine
		vimba.VmbCaptureStart( self.handle )
		# Queue the frames
		for i in range( frame_buffer_size ) :
			vimba.VmbCaptureFrameQueue( self.handle, ct.byref( self.frame_buffer[i] ), self.vmb_frame_callback )
		# Start acquisition
		vimba.VmbFeatureCommandRun( self.handle, 'AcquisitionStart' )
	# Stop the acquisition
	def StopCapture( self ) :
		# Stop acquisition
		vimba.VmbFeatureCommandRun( self.handle, 'AcquisitionStop' )
		# Flush the frame queue
		vimba.VmbCaptureQueueFlush( self.handle )
		# Stop capture engine
		vimba.VmbCaptureEnd( self.handle )
		# Revoke frames
		vimba.VmbFrameRevokeAll( self.handle )
	# Function called by Vimba to receive the frame
	def VmbFrameCallback( self, camera, frame ) :
		# Call external frame callback function
		self.frame_callback( frame.contents )
		# Requeue the frame so it can be filled again
		vimba.VmbCaptureFrameQueue( camera, frame, self.vmb_frame_callback )

# Vimba stereo camera
class VmbStereoCamera( object ) :
	# Initialize the cameras
	def __init__( self, camera_left_id, camera_right_id ) :
		self.camera_left = VmbCamera( camera_left_id )
		self.camera_right = VmbCamera( camera_right_id )
	# Open the cameras
	def Open( self ) :
		self.camera_left.Open()
		self.camera_right.Open()
	# Close the cameras
	def Close( self ) :
		self.camera_left.Close()
		self.camera_right.Close()
	# Start synchronous acquisition
	def StartCapture( self, frame_callback ) :
		# Register the external image callback function
		self.frame_callback = frame_callback
		# Initialize the frames
		self.frame_left = None
		self.frame_right = None
		# Start acquisition
		self.camera_left.StartCapture( self.FrameCallbackLeft )
		self.camera_right.StartCapture( self.FrameCallbackRight )
	# Stop the acquisition
	def StopCapture( self ) :
		self.camera_left.StopCapture()
		self.camera_right.StopCapture()
	# Receive a frame from camera left
	def FrameCallbackLeft( self, frame ) :
		# Save the current frame
		self.frame_left = frame
		# Synchronize the frames
		self.Synchronize()
	# Receive a frame from camera right
	def FrameCallbackRight( self, frame ) :
		# Save the current frame
		self.frame_right = frame
		# Synchronize the frames
		self.Synchronize()
	# Synchronize the frames from both camera
	def Synchronize( self ) :
		# Wait for both frames
		if self.frame_left and self.frame_right :
			# Send the frames to the external program
			self.frame_callback( self.frame_left, self.frame_right )
			# Initialize the frames
			self.frame_left = None
			self.frame_right = None
