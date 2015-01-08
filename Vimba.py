# -*- coding:utf-8 -*- 


#
# Interface to the AVT Vimba SDK
#


#
# External dependencies
#
import os
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
	vimba_path = "/" + "/".join(os.environ.get("GENICAM_GENTL64_PATH").split("/")[1:-3])
	vimba_path += "/VimbaC/DynamicLib/x86_64bit/libVimbaC.so"
		
	# Load Vimba library
	global vimba
	vimba = ct.cdll.LoadLibrary( vimba_path )

	# Initialize the library
	vimba.VmbStartup()
		
	# Send discovery packet to GigE cameras
	vimba.VmbFeatureCommandRun( ct.c_void_p(1), "GeVDiscoveryAllOnce" )
	

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
	_fields_ = [('buffer', ct.POINTER(ct.c_char)),
			('bufferSize', ct.c_uint32),
			('context', ct.c_void_p * 4),
			('receiveStatus', ct.c_int32),
			('receiveFlags', ct.c_uint32),
			('imageSize', ct.c_uint32),
			('ancillarySize', ct.c_uint32),
			('pixelFormat', ct.c_uint32),
			('width', ct.c_uint32),
			('height', ct.c_uint32),
			('offsetX', ct.c_uint32),
			('offsetY', ct.c_uint32),
			('frameID', ct.c_uint64),
			('timestamp', ct.c_uint64)]
	
	#
	# Initialize the image buffer
	#
	def __init__( self, frame_size ) :

		self.buffer = ct.create_string_buffer( frame_size )
		self.bufferSize = ct.c_uint32( frame_size )


#
# Vimba camera
#
class VmbCamera( object ) :
	
	#
	# Initialize the camera
	#
	def __init__( self, id_string ) :
		
		# Camera handle
		self.handle = ct.c_void_p()

		# Camera ID (serial number, IP address...)
		self.id_string = id_string
		
		# Connect the camera
		vimba.VmbCameraOpen( self.id_string, 1, ct.byref(self.handle) )

		# Adjust packet size automatically
		vimba.VmbFeatureCommandRun( self.handle, "GVSPAdjustPacketSize" )
		
		# Configure the camera
		vimba.VmbFeatureEnumSet( self.handle, "AcquisitionMode", "Continuous" )
		vimba.VmbFeatureEnumSet( self.handle, "TriggerSource", "Freerun" )
		vimba.VmbFeatureEnumSet( self.handle, "PixelFormat", "Mono8" )

		# Query image parameters
		tmp_value = ct.c_int()
		vimba.VmbFeatureIntGet( self.handle, "Width", ct.byref(tmp_value) )
		self.width = tmp_value.value
		vimba.VmbFeatureIntGet( self.handle, "Height", ct.byref(tmp_value) )
		self.height = tmp_value.value
		vimba.VmbFeatureIntGet( self.handle, "PayloadSize", ct.byref(tmp_value) )
		self.payloadsize = tmp_value.value
		
		# Default image parameters of our cameras (AVT Manta G504B) for debug purpose
		self.width = 2452
		self.height = 2056
		self.payloadsize = 5041312

		# Initialize the image
		self.image = np.zeros( (self.height, self.width), dtype=np.uint8 )	
	
		# Initialize frame buffer
		self.frame_number = 3
		self.frames = []
		for i in range( self.frame_number ) :
			self.frames.append( VmbFrame( self.payloadsize ) )
		
	#
	# Disconnect the camera
	#
	def Disconnect( self ) :
		
		# Close the camera
		vimba.VmbCameraClose( self.handle )

	#
	# Start the acquisition
	#
	def CaptureStart( self, ProcessImage = None ) :
		
		# Asynchronous capture (if any)
		self.frame_callback_function = None
		if ProcessImage :
			self.frame_callback_function = self.CreateFrameCallbackFunction( ProcessImage )

		# Announce the frames
		for i in range( self.frame_number ) :
			vimba.VmbFrameAnnounce( self.handle, ct.byref(self.frames[i]), ct.sizeof(self.frames[i]) )

		# Start capture engine
		vimba.VmbCaptureStart( self.handle )
		
		# Queue the frames
		for i in range( self.frame_number ) :
			vimba.VmbCaptureFrameQueue( self.handle, ct.byref(self.frames[i]), self.frame_callback_function )

		# Initialize frame buffer index
		self.frame_index = 0
		
		# Start acquisition
		vimba.VmbFeatureCommandRun( self.handle, "AcquisitionStart" )

	#
	# Capture a synchronous frame
	#
	def CaptureFrame( self ) :
		
		# Capture a frame
		vimba.VmbCaptureFrameWait( self.handle, ct.byref(self.frames[self.frame_index]), 1000 )
		
		# Check frame validity
		if self.frames[self.frame_index].receiveStatus :	
			print( 'Invalid frame received... {}'.format(self.frames[self.frame_index].receiveStatus) )
			
		# Convert frame to numpy arrays
		self.image = np.fromstring( self.frames[self.frame_index].buffer[ 0 : self.payloadsize ], dtype=np.uint8 ).reshape( self.height, self.width )

		# Requeue frame
		vimba.VmbCaptureFrameQueue( self.handle, ct.byref(self.frames[self.frame_index]), None )
		
		# Next frame
		self.frame_index += 1
		if self.frame_index == self.frame_number :
			self.frame_index = 0

	#
	# Stop the acquisition
	#
	def CaptureStop( self ) :

		# Stop acquisition
		vimba.VmbFeatureCommandRun( self.handle, "AcquisitionStop" )

		# Flush the frame queue
		vimba.VmbCaptureQueueFlush( self.handle )

		# Stop capture engine
		vimba.VmbCaptureEnd( self.handle )

		# Revoke frames
		vimba.VmbFrameRevokeAll( self.handle )
		
	#
	# Create a frame callback function
	#
	def CreateFrameCallbackFunction( self, ProcessImage ) :
		
		# Define the frame callback function
		def FrameCallback( camera, frame ) :

			# Print frame informations
			print( 'Frame callback - Frame ID : {} - Status : {}...'.format(frame.contents.frameID, frame.contents.receiveStatus) )
				
			# Convert frames to numpy arrays
			self.image = np.fromstring( frame.contents.buffer[ 0 : self.payloadsize ], dtype=np.uint8 ).reshape( self.height, self.width )
			
			# Process the image with the provided function
			ProcessImage( self.image )

			# Requeue the frame so it can be filled again
			vimba.VmbCaptureFrameQueue( camera, frame, self.frame_callback_function )
			
		# Register the callback function
		return ct.CFUNCTYPE( None, ct.c_void_p, ct.POINTER(VmbFrame) )( FrameCallback )

	#
	# Print camera statistics
	#
	def PrintStats( self ) :
		
		# Temporary variables
		tmp_int = ct.c_int()
		tmp_float = ct.c_double()
		stats = []
		
		# Get some camera statistics
		vimba.VmbFeatureIntGet( self.handle, "StatFrameDelivered", ct.byref(tmp_int) )
		stats.append( tmp_int.value )
		vimba.VmbFeatureIntGet( self.handle, "StatFrameDropped", ct.byref(tmp_int) )
		stats.append( tmp_int.value )
		vimba.VmbFeatureIntGet( self.handle, "StatPacketReceived", ct.byref(tmp_int) )
		stats.append( tmp_int.value )
		vimba.VmbFeatureIntGet( self.handle, "StatPacketMissed", ct.byref(tmp_int) )
		stats.append( tmp_int.value )
		vimba.VmbFeatureFloatGet( self.handle, "StatLocalRate", ct.byref(tmp_float) )
		stats.append( tmp_float.value )
		
		# Print camera statistics
		print( "Camera {} - FrmDvd : {}  FrmDrp : {} PckRvd : {} PckMss : {} FrmRt : {:.2f}".format( self.id_string, stats[0], stats[1], stats[2], stats[3], stats[4] ) )
