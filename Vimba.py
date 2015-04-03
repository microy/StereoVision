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
	def __init__( self, id_string, pixel_format = "Mono8", jumbo_frame = True ) :
		
		# Camera handle
		self.handle = ct.c_void_p()

		# Camera ID (serial number, IP address...)
		self.id_string = id_string
		
		# Connect the camera
		vimba.VmbCameraOpen( self.id_string, 1, ct.byref(self.handle) )

		# Jumbo frames - Force the MTU to 9000 bytes
		if jumbo_frame : vimba.VmbFeatureIntSet( self.handle, "GVSPPacketSize", 9000 )
			
		# Or adjust packet size automatically
		else : vimba.VmbFeatureCommandRun( self.handle, "GVSPAdjustPacketSize" )

		# Configure the image format
		self.pixel_format = pixel_format
		vimba.VmbFeatureEnumSet( self.handle, "PixelFormat", self.pixel_format )

		# Query image parameters
		tmp_value = ct.c_int()
		vimba.VmbFeatureIntGet( self.handle, "Width", ct.byref(tmp_value) )
		self.width = tmp_value.value
		vimba.VmbFeatureIntGet( self.handle, "Height", ct.byref(tmp_value) )
		self.height = tmp_value.value
		vimba.VmbFeatureIntGet( self.handle, "PayloadSize", ct.byref(tmp_value) )
		self.payloadsize = tmp_value.value
		
		# Default image parameters of our cameras (AVT Manta G504B) for debug purpose
#		self.width = 2452
#		self.height = 2056
#		self.payloadsize = 5041312

		# Initialize the image
		if self.pixel_format == "Mono8" :
			self.image = np.zeros( (self.height, self.width), dtype=np.uint8 )
		elif self.pixel_format == "Mono12" :
			self.image = np.zeros( (self.height, self.width), dtype=np.uint16 )

	#
	# Disconnect the camera
	#
	def Disconnect( self ) :
		
		# Close the camera
		vimba.VmbCameraClose( self.handle )

	#
	# Start asynchronous acquisition
	#
	def StartCapture( self, image_callback_function, buffer_count = 3 ) :

		# Configure freerun trigger (full camera speed)
		vimba.VmbFeatureEnumSet( self.handle, "TriggerSource", "Freerun" )
		
		# Initialize frame buffer
		self.frame_buffer = []
		for i in range( buffer_count ) :
			self.frame_buffer.append( VmbFrame( self.payloadsize ) )
		
		# Register the external image callback function
		self.image_callback_function = image_callback_function
		
		# Register the internal frame callback function
		self.frame_callback_function = ct.CFUNCTYPE( None, ct.c_void_p, ct.POINTER(VmbFrame) )( self.FrameCallback )

		# Announce the frames
		for i in range( buffer_count ) :
			vimba.VmbFrameAnnounce( self.handle, ct.byref(self.frame_buffer[i]), ct.sizeof(self.frame_buffer[i]) )

		# Start capture engine
		vimba.VmbCaptureStart( self.handle )
		
		# Queue the frames
		for i in range( buffer_count ) :
			vimba.VmbCaptureFrameQueue( self.handle, ct.byref(self.frame_buffer[i]), self.frame_callback_function )

		# Reset the camera timestamp
		vimba.VmbFeatureCommandRun( self.handle, "GevTimestampControlReset" )

		# Start acquisition
		vimba.VmbFeatureCommandRun( self.handle, "AcquisitionStart" )
		
	#
	# Frame callback function called by Vimba
	#
	def FrameCallback( self, camera, frame ) :

		# Check frame validity
		if not frame.contents.receiveStatus :

			# Save the image timestamp
			self.timestamp = frame.contents.timestamp
			
			# Convert de 8 bit frame to image
			if self.pixel_format == "Mono8" :
				
				# Convert frames to numpy arrays
				self.image = np.fromstring( frame.contents.buffer[ 0 : self.payloadsize ], dtype=np.uint8 )
				self.image = self.image.reshape( self.height, self.width )

			# Convert the 12 bit frame to image
			elif self.pixel_format == "Mono12" :

				# Convert frames to numpy arrays
				self.image = np.fromstring( frame.contents.buffer[ 0 : self.payloadsize ], dtype=np.uint16 )
				self.image = self.image.reshape( self.height, self.width )
				
				# Convert 12 bits image to 16 bits image
				self.image = (self.image.astype(np.float) * 0xFFFF / 0xFFF).astype(np.uint16)
			
			# Call foreign image processing function
			self.image_callback_function()

		# Requeue the frame so it can be filled again
		vimba.VmbCaptureFrameQueue( camera, frame, self.frame_callback_function )

	#
	# Stop the acquisition
	#
	def StopCapture( self ) :

		# Stop acquisition
		vimba.VmbFeatureCommandRun( self.handle, "AcquisitionStop" )

		# Flush the frame queue
		vimba.VmbCaptureQueueFlush( self.handle )

		# Stop capture engine
		vimba.VmbCaptureEnd( self.handle )

		# Revoke frames
		vimba.VmbFrameRevokeAll( self.handle )
		

#
# Vimba stereo camera
#
class VmbStereoCamera( object ) :
	
	#
	# Initialize the cameras
	#
	def __init__( self, camera_1_id, camera_2_id ) :

		# Camera connection
		self.camera_1 = VmbCamera( camera_1_id )
		self.camera_2 = VmbCamera( camera_2_id )

	#
	# Disconnect the cameras
	#
	def Disconnect( self ) :
		
		# Close the cameras
		self.camera_1.Disconnect()
		self.camera_2.Disconnect()

	#
	# Start synchronous acquisition
	#
	def StartCapture( self ) :
		
		# Create the image frames
		self.frame_1 = VmbFrame( self.camera_1.payloadsize )
		self.frame_2 = VmbFrame( self.camera_2.payloadsize )

		# Configure frame software trigger
		vimba.VmbFeatureEnumSet( self.camera_1.handle, "TriggerSource", "Software" )
		vimba.VmbFeatureEnumSet( self.camera_2.handle, "TriggerSource", "Software" )

		# Announce the frames
		vimba.VmbFrameAnnounce( self.camera_1.handle, ct.byref(self.frame_1), ct.sizeof(self.frame_1) )
		vimba.VmbFrameAnnounce( self.camera_2.handle, ct.byref(self.frame_2), ct.sizeof(self.frame_2) )

		# Start capture engine
		vimba.VmbCaptureStart( self.camera_1.handle )
		vimba.VmbCaptureStart( self.camera_2.handle )
		
		# Start acquisition
		vimba.VmbFeatureCommandRun( self.camera_1.handle, "AcquisitionStart" )
		vimba.VmbFeatureCommandRun( self.camera_2.handle, "AcquisitionStart" )
		
	#
	# Capture a frame on both cameras
	#
	def CaptureFrames( self ) :
		
		# Capture frames until both are valid
		while True :
			
			# Queue frames
			vimba.VmbCaptureFrameQueue( self.camera_1.handle, ct.byref(self.frame_1), None )
			vimba.VmbCaptureFrameQueue( self.camera_2.handle, ct.byref(self.frame_2), None )
			
			# Send software trigger
			vimba.VmbFeatureCommandRun( self.camera_1.handle, "TriggerSoftware" )
			vimba.VmbFeatureCommandRun( self.camera_2.handle, "TriggerSoftware" )

			# Get frames back
			vimba.VmbCaptureFrameWait( self.camera_1.handle, ct.byref(self.frame_1), 1000 )
			vimba.VmbCaptureFrameWait( self.camera_2.handle, ct.byref(self.frame_2), 1000 )

			# If both frames are valid, stop here
			if not (self.frame_1.receiveStatus or self.frame_2.receiveStatus) : break
		
		# Convert frames to numpy arrays
		image_1 = np.fromstring( self.frame_1.buffer[ 0 : self.camera_1.payloadsize ], dtype=np.uint8 )
		image_1 = image_1.reshape( self.camera_1.height, self.camera_1.width )
		image_2 = np.fromstring( self.frame_2.buffer[ 0 : self.camera_2.payloadsize ], dtype=np.uint8 )
		image_2 = image_2.reshape( self.camera_2.height, self.camera_2.width )
		
		# Return images from both camera
		return image_1, image_2

	#
	# Stop the acquisition
	#
	def StopCapture( self ) :

		# Stop image acquisition
		self.camera_1.StopCapture()
		self.camera_2.StopCapture()

