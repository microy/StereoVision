# -*- coding:utf-8 -*- 


#
# Module to display live images from AVT cameras
#


#
# External dependencies
#
import ctypes as ct
import threading
import cv2
import numpy as np
import Vimba
import Calibration



#
# Vimba camera viewer
#
class Viewer( object ) :
	
	#
	# Initialization
	#
	def __init__( self, camera ) :
		
		# Register the camera to display
		self.camera = camera
		
		# Active live chessboard finding and drawing on the image
		self.calibration_enabled = True
				
	#
	# Start capture and display image stream
	#
	def LiveDisplay( self ) :

		# Start image acquisition
		self.capturing = True
		self.camera.CaptureStart( self.ImageCallback )
		
		# Keyboard interruption
		while self.capturing : pass

		# Stop image acquisition
		self.camera.CaptureStop()

		# Cleanup OpenCV
		cv2.destroyWindow( self.camera.id_string )

	#
	# Display the current image
	#
	def ImageCallback( self, image ) :
		
		# Resize image for display
		image_displayed = cv2.resize( image, None, fx=0.3, fy=0.3 )

		# Preview the calibration chessboard on the image
		if self.calibration_enabled :
			Calibration.PreviewChessboard( image_displayed )
		
		# Display the image (scaled down)
		cv2.imshow( self.camera.id_string, image_displayed )

		# Keyboard interruption
		if ( cv2.waitKey(1) & 0xFF ) == 27 :
			self.capturing = False


#
# Vimba stereo camera viewer (asynchronous)
#
class StereoViewer( object ) :
	
	#
	# Initialization
	#
	def __init__( self, camera_1, camera_2 ) :
		
		# Register the camera to display
		self.camera_1 = camera_1
		self.camera_2 = camera_2
	
		# Image parameters
		self.width = camera_1.width
		self.height = camera_1.height
		
		# Lock for data synchronisation
		self.lock = threading.Lock()

		# Live image of both cameras
		self.stereo_image = np.zeros( (self.height, 2*self.width), dtype=np.uint8 )
		
		# Number of images saved
		self.image_count = 0
		
	#
	# Start capture and display image stream
	#
	def LiveDisplay( self ) :

		# Start image acquisition
		self.capturing = True
		self.camera_1.CaptureStart( self.ImageCallback_1 )
		self.camera_2.CaptureStart( self.ImageCallback_2 )
		
		# Keyboard interruption
		while self.capturing : pass

		# Stop image acquisition
		self.camera_1.CaptureStop()
		self.camera_2.CaptureStop()

		# Cleanup OpenCV
		cv2.destroyAllWindows()

	#
	# Display the current image for camera 1
	#
	def ImageCallback_1( self, image ) :
		
		# Lock the thread
		self.lock.acquire()
		
		# Put the current image in the combined image
		self.stereo_image[ 0:self.height, 0:self.width ] = image
		
		# Resize image for display
		image_displayed = cv2.resize( self.stereo_image, None, fx=0.3, fy=0.3 )
		
		# Release the thread
		self.lock.release()

		# Display the image (scaled down)
		cv2.imshow( "Stereo", image_displayed )

		# Keyboard interruption
		if ( cv2.waitKey(1) & 0xFF ) == 27 :
			self.capturing = False

	#
	# Display the current image for camera 2
	#
	def ImageCallback_2( self, image ) :
		
		# Lock the thread
		self.lock.acquire()
		
		# Put the current image in the combined image
		self.stereo_image[ 0:self.height, self.width:2*self.width ] = image

		# Resize image for display
		image_displayed = cv2.resize( self.stereo_image, None, fx=0.3, fy=0.3 )
		
		# Release the thread
		self.lock.release()

		# Display the image (scaled down)
		cv2.imshow( "Stereo", image_displayed )

		# Keyboard interruption
		if ( cv2.waitKey(1) & 0xFF ) == 27 :
			self.capturing = False


#
# Vimba stereo camera viewer (synchronous)
#
class StereoViewerSync( object ) :
	
	#
	# Initialization
	#
	def __init__( self, camera_1, camera_2 ) :
		
		# Register the camera to display
		self.camera_1 = camera_1
		self.camera_2 = camera_2
	
		# Image parameters
		self.width = camera_1.width
		self.height = camera_1.height
		
		# Image frames
		self.frame_1 = Vimba.VmbFrame( camera_1.payloadsize )
		self.frame_2 = Vimba.VmbFrame( camera_1.payloadsize )

		# Live image of both cameras
		self.stereo_image = np.zeros( (self.height, 2*self.width), dtype=np.uint8 )
		
		# Configure frame software trigger
		Vimba.vimba.VmbFeatureEnumSet( self.camera_1.handle, "TriggerSource", "Software" )
		Vimba.vimba.VmbFeatureEnumSet( self.camera_2.handle, "TriggerSource", "Software" )

	#
	# Start capture and display image stream
	#
	def LiveDisplay( self ) :

		# Number of images saved
		image_count = 0
		
		# Announce the frames
		Vimba.vimba.VmbFrameAnnounce( self.camera_1.handle, ct.byref(self.frame_1), ct.sizeof(self.frame_1) )
		Vimba.vimba.VmbFrameAnnounce( self.camera_2.handle, ct.byref(self.frame_2), ct.sizeof(self.frame_2) )

		# Start capture engine
		Vimba.vimba.VmbCaptureStart( self.camera_1.handle )
		Vimba.vimba.VmbCaptureStart( self.camera_2.handle )

		# Start acquisition
		Vimba.vimba.VmbFeatureCommandRun( self.camera_1.handle, "AcquisitionStart" )
		Vimba.vimba.VmbFeatureCommandRun( self.camera_2.handle, "AcquisitionStart" )

		# Live display
		while True :
			
			# Queue frames
			Vimba.vimba.VmbCaptureFrameQueue( self.camera_1.handle, ct.byref(self.frame_1), None )
			Vimba.vimba.VmbCaptureFrameQueue( self.camera_2.handle, ct.byref(self.frame_2), None )
			
			# Send software trigger
			Vimba.vimba.VmbFeatureCommandRun( self.camera_1.handle, "TriggerSoftware" )
			Vimba.vimba.VmbFeatureCommandRun( self.camera_2.handle, "TriggerSoftware" )

			# Get frames back
			Vimba.vimba.VmbCaptureFrameWait( self.camera_1.handle, ct.byref(self.frame_1), 1000 )
			Vimba.vimba.VmbCaptureFrameWait( self.camera_2.handle, ct.byref(self.frame_2), 1000 )
			
			# Check frame validity
			if self.frame_1.receiveStatus or self.frame_2.receiveStatus :
				continue
			
			# Convert frames to numpy arrays
			image_1 = np.fromstring( self.frame_1.buffer[ 0 : self.camera_1.payloadsize ], dtype=np.uint8 ).reshape( self.height, self.width )
			image_2 = np.fromstring( self.frame_2.buffer[ 0 : self.camera_1.payloadsize ], dtype=np.uint8 ).reshape( self.height, self.width )

			# Prepare image for display
			self.stereo_image[ 0:self.height, 0:self.width ] = image_1
			self.stereo_image[ 0:self.height, self.width:2*self.width ] = image_2
			
			# Resize image for display
			image_final = cv2.resize( self.stereo_image, None, fx=0.3, fy=0.3 )

			# Display the image (scaled down)
			cv2.imshow( "Stereo Cameras", image_final )
			
			# Keyboard interruption
			key = cv2.waitKey(1) & 0xFF
			
			# Escape key
			if key == 27 :
				
				# Exit live display
				break
				
			# Space key
			elif key == 32 :
				
				# Save images to disk 
				image_count += 1
				print( 'Save images {} to disk...'.format(image_count) )
				cv2.imwrite( 'camera1-{:0>2}.png'.format(image_count), image_1 )
				cv2.imwrite( 'camera2-{:0>2}.png'.format(image_count), image_2 )


		# Stop image acquisition
		self.camera_1.CaptureStop()
		self.camera_2.CaptureStop()
					
		# Cleanup OpenCV
		cv2.destroyAllWindows()


