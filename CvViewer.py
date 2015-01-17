# -*- coding:utf-8 -*- 


#
# Module to display live images from AVT cameras
#


#
# External dependencies
#
import cv2
import Calibration

# Display scale factor
scale_factor = 0.35

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
		self.chessboard_enabled = False
		
		# Saved image counter
		self.image_count = 0
				
	#
	# Start capture and display image stream
	#
	def LiveDisplay( self ) :

		# Start image acquisition
		self.capturing = True
		self.camera.StartCaptureAsync( self.ImageCallback )
		
		# Streaming loop
		while self.capturing : pass

		# Stop image acquisition
		self.camera.StopCapture()

		# Cleanup OpenCV
		cv2.destroyAllWindows()

	#
	# Display the current image
	#
	def ImageCallback( self, image ) :
		
		# Resize image for display
		image_displayed = cv2.resize( image, None, fx=scale_factor, fy=scale_factor )

		# Preview the calibration chessboard on the image
		if self.chessboard_enabled :
			image_displayed = Calibration.PreviewChessboard( image_displayed )
		
		# Display the image (scaled down)
		cv2.imshow( self.camera.id_string, image_displayed )
		
		# Keyboard interruption
		key = cv2.waitKey( 10 ) & 0xFF
			
		# Escape key
		if key == 27 :
			
			# Exit live display
			self.capturing = False
			
		# Space key
		elif key == 32 :
			
			# Save image to disk 
			self.image_count += 1
			print( 'Save image {} to disk...'.format(self.image_count) )
			cv2.imwrite( 'camera-{}-{:0>2}.png'.format(self.camera.id_string, self.image_count), image )
			
		# C key
		elif key == ord('c') :
			
			# Enable / Disable chessboard preview
			self.chessboard_enabled = not self.chessboard_enabled


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
		
		# Active live chessboard finding and drawing on the image
		self.chessboard_enabled = False
		
		# Saved image counter
		self.image_count = 0

	#
	# Start capture and display image stream
	#
	def LiveDisplay( self ) :

		# Start image acquisition
		self.capturing = True
		self.camera_1.StartCaptureAsync( self.ImageCallback_1 )
		self.camera_2.StartCaptureAsync( self.ImageCallback_2 )
		
		# Streaming loop
		while self.capturing : pass

		# Stop image acquisition
		self.camera_1.StopCapture()
		self.camera_2.StopCapture()

		# Cleanup OpenCV
		cv2.destroyAllWindows()
		
	#
	# Save images from both cameras to disk
	#
	def SaveImages( self ) :
		
		# Count images
		self.image_count += 1
		
		# Save image to disk 
		print( 'Save image {} to disk...'.format(self.image_count) )
		cv2.imwrite( 'camera-1-{:0>2}.png'.format(self.image_count), self.image_1 )
		cv2.imwrite( 'camera-2-{:0>2}.png'.format(self.image_count), self.image_2 )

	#
	# Display the current image for camera 1
	#
	def ImageCallback_1( self, image ) :

		# Backup current image
		self.image_1 = image

		# Resize image for display
		image_displayed = cv2.resize( image, None, fx=scale_factor, fy=scale_factor )
		
		# Preview the calibration chessboard on the image
		if self.chessboard_enabled :
			image_displayed = Calibration.PreviewChessboard( image_displayed )

		# Display the image (scaled down)
		cv2.imshow( "Camera 1", image_displayed )

		# Keyboard interruption
		self.KeyboardEvent()

	#
	# Display the current image for camera 2
	#
	def ImageCallback_2( self, image ) :

		# Backup current image
		self.image_2 = image
		
		# Resize image for display
		image_displayed = cv2.resize( image, None, fx=scale_factor, fy=scale_factor )

		# Preview the calibration chessboard on the image
		if self.chessboard_enabled :
			image_displayed = Calibration.PreviewChessboard( image_displayed )

		# Display the image (scaled down)
		cv2.imshow( "Camera 2", image_displayed )

		# Keyboard interruption
		self.KeyboardEvent()

	#
	# Keyboard event
	#
	def KeyboardEvent( self ) :

		# Keyboard interruption
		key = cv2.waitKey( 10 ) & 0xFF
			
		# Escape key
		if key == 27 :
			
			# Exit live display
			self.capturing = False
			
		# Space key
		elif key == 32 :

			# Save images to disk
			self.SaveImages()
			
		# C ke
		elif key == ord('c') :
			
			# Enable / Disable chessboard preview
			self.chessboard_enabled = not self.chessboard_enabled



import ctypes as ct
import numpy as np
import Vimba

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
		
		
		

#
# Vimba stereo camera viewer (synchronous)
# with separate camera threads
#
class StereoViewerSync2( object ) :
	
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
		
		# Live image of both cameras
		self.stereo_image = np.zeros( (self.height, 2*self.width), dtype=np.uint8 )
		
		# Configure camera software trigger thread
		self.camera_1_thread = TriggerAcquisitionThread( self.camera_1 )
		self.camera_2_thread = TriggerAcquisitionThread( self.camera_2 )

	#
	# Start capture and display image stream
	#
	def LiveDisplay( self ) :

		# Number of images saved
		image_count = 0
		
		# Start acquisition
		self.camera_1_thread.Start()
		self.camera_2_thread.Start()

		# Live display
		while True :
			
			# Send software trigger to both cameras
			self.camera_1_thread.TriggerUp()
			self.camera_2_thread.TriggerUp()
			
			# Wait for images
			while not self.camera_1_thread.ImageReceived() and not self.camera_2_thread.ImageReceived() : pass
			
			# Prepare image for display
			self.stereo_image[ 0:self.height, 0:self.width ] = self.camera_1.image
			self.stereo_image[ 0:self.height, self.width:2*self.width ] = self.camera_2.image
			
			# Resize image for display
			image_displayed = cv2.resize( self.stereo_image, None, fx=0.3, fy=0.3 )

			# Display the image (scaled down)
			cv2.imshow( "Stereo Cameras", image_displayed )
			
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
				cv2.imwrite( 'camera1-{:0>2}.png'.format(image_count), self.camera_1.image )
				cv2.imwrite( 'camera2-{:0>2}.png'.format(image_count), self.camera_2.image )


		# Stop image acquisition
		self.camera_1_thread.Stop()
		self.camera_2_thread.Stop()
					
		# Cleanup OpenCV
		cv2.destroyAllWindows()


import threading


#
# Software trigger acquisition thread
#
class TriggerAcquisitionThread( threading.Thread ) :
	
	#
	# Initialisation
	#
	def __init__( self, camera ) :
		
		# Initialise the thread
		threading.Thread.__init__( self )
		
		# The camera
		self.camera = camera

	#
	# Preview the chessboard in a separate thread
	#
	def Start( self ) :

		# Start synchronous image capture
		self.camera.StartCaptureSync()
		
		# Image acquisition running
		self.capturing = True
		
		# The camera trigger
		self.trigger = False
		
		# Start the thread
		self.start()

	#
	# Preview the chessboard in a separate thread
	#
	def Stop( self ) :

		# Stop the thread
		self.capturing = False
		self.join()
		
		# Stop image acquisition
		self.camera.StopCapture()
		
	#
	# Activate the triger
	#
	def TriggerUp( self ) :
		
		self.trigger = True

	#
	# Tell if the single image acquisition is done
	#
	def ImageReceived( self ) :
		
		return not self.trigger

	#
	# Acquire an image on trigger
	#
	def run( self ) :
		
		# Image acquisition
		while self.capturing :

			# Trigger up
			if self.trigger :
				
				# Capture the image
				if self.camera.CaptureImageSync() :
				
					# Trigger down
					self.trigger = False


