#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Interface to the AVT Vimba SDK
#


#
# External dependencies
#
import collections, cv2, os, time
import ctypes as ct
import numpy as np


#
# Access to the Vimba C library
#
class VmbSystem( object ) :

	# Initialize the Vimba driver
	def Startup( self ) :

		# Get Vimba installation directory
		vimba_path = "/" + "/".join(os.environ.get("GENICAM_GENTL64_PATH").split("/")[1:-3])
		vimba_path += "/VimbaC/DynamicLib/x86_64bit/libVimbaC.so"
			
		# Load Vimba library
		self.vimba = ct.cdll.LoadLibrary( vimba_path )

		# Initialize the library
		self.vimba.VmbStartup()
			
		# Send discovery packet to GigE cameras
		self.vimba.VmbFeatureCommandRun( ct.c_void_p(1), "GeVDiscoveryAllOnce" )

	# Release the Vimba driver
	def Shutdown( self ):
		
		# Release the library
		self.vimba.VmbShutdown()


#
# Vimba frame structure
#
class VmbFrame( ct.Structure ) :
	
	# VmbFrame structure fields
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
	
	# Initialize the image buffer
	def __init__( self, frame_size ) :

		self.buffer = ct.create_string_buffer( frame_size )
		self.bufferSize = ct.c_uint32( frame_size )


#
# Vimba camera
#
class VmbCamera( object ) :
	
	# Default image parameters of our cameras (AVT Manta G504B)
	width = 2452
	height = 2056
	payloadsize = 5041312
	
	# Initialisation
	def __init__( self, vimba_system ) :
		
		# Vimba handle
		self.vimba = vimba_system.vimba
		
		# Camera handle
		self.handle = ct.c_void_p()
	
	# Connect to a camera using its ID (serial number, IP address...)
	def Connect( self, id_string ) :
		
		# Backup camera ID
		self.id_string = id_string
		
		# Connect the camera
		self.vimba.VmbCameraOpen( id_string, 1, ct.byref(self.handle) )

		# Adjust packet size automatically
		self.vimba.VmbFeatureCommandRun( self.handle, "GVSPAdjustPacketSize" )
		
		# Initialize the image
		self.image = np.zeros( (self.height, self.width), dtype=np.uint8 )	
	
	# Disconnect the camera
	def Disconnect( self ) :
		
		# Close the camera
		self.vimba.VmbCameraClose( self.handle )

	# Start the acquisition
	def CaptureStart( self ) :

		# Create an image frame
		self.frame = VmbFrame( self.payloadsize )
		
		# Announce the frames
		self.vimba.VmbFrameAnnounce( self.handle, ct.byref(self.frame), ct.sizeof(self.frame) )

		# Start capture engine
		self.vimba.VmbCaptureStart( self.handle )

		# Queue a frame
		self.vimba.VmbCaptureFrameQueue( self.handle, ct.byref(self.frame), None )

		# Start acquisition
		self.vimba.VmbFeatureCommandRun( self.handle, "AcquisitionStart" )

	# Capture a frame
	def CaptureFrame( self ) :
		
		# Capture a frame
		self.vimba.VmbCaptureFrameWait( self.handle, ct.byref(self.frame), 1000 )
		
		# Check frame validity
		if self.frame.receiveStatus :
			print( 'Invalid frame status...' )
			return
		
		# Convert frame to numpy arrays
		self.image = np.fromstring( self.frame.buffer[ 0 : self.payloadsize ], dtype=np.uint8 ).reshape( self.height, self.width )

		# Queue another frame
		self.vimba.VmbCaptureFrameQueue( self.handle, ct.byref(self.frame), None )

	# Stop the acquisition
	def CaptureStop( self ) :

		# Stop acquisition
		self.vimba.VmbFeatureCommandRun( self.handle, "AcquisitionStop" )

		# Flush the frame queue
		self.vimba.VmbCaptureQueueFlush( self.handle )

		# Stop capture engine
		self.vimba.VmbCaptureEnd( self.handle )

		# Revoke frames
		self.vimba.VmbFrameRevokeAll( self.handle )

	# Start the acquisition asynchronously
	def CaptureStartAsync( self ) :

		# Create 3 frames to fill in the camera buffer
		frames = 3 * [ VmbFrame( self.payloadsize ) ]

		# Reference to frame callback function
		self.frame_callback_function = self.GetFrameCallbackFunction()

		# Announce the frames
		for i in range( 3 ) :
			self.vimba.VmbFrameAnnounce( self.handle, ct.byref(frames[i]), ct.sizeof(frames[i]) )
			
		# Start capture engine
		self.vimba.VmbCaptureStart( self.handle )

		# Queue frames
		for i in range( 3 ) :
			self.vimba.VmbCaptureFrameQueue( self.handle, ct.byref(frames[i]), self.frame_callback_function )
	
		# Start acquisition
		self.vimba.VmbFeatureCommandRun( self.handle, "AcquisitionStart" )
		
	# Create a frame callback function
	def GetFrameCallbackFunction( self ) :

		# Define the frame callback function
		def FrameCallback( camera, frame ) :

			# Print frame informations
			print( 'Frame callback - Frame ID : ', frame.contents.frameID )
				
			# Check frame validity
			if frame.contents.receiveStatus :
				print( 'Invalid frame status...' )
				return

			# Convert frames to numpy arrays
			self.image = np.fromstring( frame.contents.buffer[ 0 : self.payloadsize ], dtype=np.uint8 ).reshape( self.height, self.width )

			# Requeue the frame so it can be filled again
			self.vimba.VmbCaptureFrameQueue( camera, frame, self.frame_callback_function )

		# Return a C-type handle to the frame callback function
		return ct.CFUNCTYPE( None, ct.c_void_p, ct.c_void_p )( FrameCallback )

	# Live display
	def LiveDisplay( self ) :
		
		# Frame per second counter
		fps_counter = 1.0
		fps_buffer = collections.deque( 10*[1.0], 10 )

		# Start image acquisition
		self.CaptureStart()

		# Start live display
		while True :
			
			# Initialize the clock for counting the number of frames per second
			time_start = time.clock()

			# Capture an image
			self.CaptureFrame()
			
			# Resize image for display
			image_live = cv2.resize( self.image, None, fx=0.3, fy=0.3 )

			# Write FPS counter on the live image
			cv2.putText( image_live, '{:.2f} FPS'.format( fps_counter ), (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255) )

			# Display the image
			cv2.imshow( "Camera {}".format(self.id_string), image_live )
			
			# Keyboard interruption
			key = cv2.waitKey(1) & 0xFF
			
			# Escape key
			if key == 27 :
				
				# Exit live display
				break
				
			# Frames per second counter
			fps_buffer.pop()
			fps_buffer.appendleft( time.clock() - time_start )
			fps_counter = 10.0 / sum( fps_buffer )

		# Cleanup OpenCV
		cv2.destroyAllWindows()

		# Stop image acquisition
		self.CaptureStop()
