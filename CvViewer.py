# -*- coding:utf-8 -*- 


#
# Module to display live images from AVT cameras
#


#
# External dependencies
#
import ctypes as ct
import cv2
import numpy as np
import Calibration
import Vimba


#
# Image scale factor for display
#
scale_factor = 0.3


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
		self.camera.StartCapture( self.ImageCallback )
		
		# Streaming loop
		while self.capturing : pass

		# Stop image acquisition
		self.camera.StopCapture()

		# Cleanup OpenCV
		cv2.destroyAllWindows()

	#
	# Display the current image
	#
	def ImageCallback( self ) :
		
		# Resize image for display
		image_displayed = cv2.resize( self.camera.image, None, fx=scale_factor, fy=scale_factor )

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
			cv2.imwrite( 'camera-{}-{:0>2}.png'.format(self.camera.id_string, self.image_count), self.camera.image )
			
		# C key
		elif key == ord('c') :
			
			# Enable / Disable chessboard preview
			self.chessboard_enabled = not self.chessboard_enabled


#
# Vimba stereo camera viewer (asynchronous)
#
class StereoViewerAsync( object ) :
	
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
		self.image_1_ready = False
		self.image_2_ready = False
		self.camera_1.StartCapture( self.ImageCallback_1 )
		self.camera_2.StartCapture( self.ImageCallback_2 )
		
		# Streaming loop
		while self.capturing : pass

		# Stop image acquisition
		self.camera_1.StopCapture()
		self.camera_2.StopCapture()

		# Cleanup OpenCV
		cv2.destroyAllWindows()
		
	#
	# Retreive the current image from camera 1
	#
	def ImageCallback_1( self ) :

		# Backup current image
		self.image_1 = self.camera_1.image
		self.timestamp_1 = self.camera_1.timestamp

		# Image ready
		self.image_1_ready = True
		
		# Synchronize both images
		self.SynchronizeImages()

	#
	# Retreive the current image from camera 2
	#
	def ImageCallback_2( self ) :

		# Backup current image
		self.image_2 = self.camera_2.image
		self.timestamp_2 = self.camera_2.timestamp
		
		# Image ready
		self.image_2_ready = True
		
		# Synchronize both images
		self.SynchronizeImages()

	#
	# Synchronize images from both cameras
	#
	def SynchronizeImages( self ) :
		
		# Check if both images are ready
		if self.image_1_ready and self.image_2_ready :
			
			# Check timestamps difference
			#if math.abs(left_time - right_time) <= max_nsec_sync_error :
			#print( abs( self.timestamp_1 - self.timestamp_2 ) )

			# Resize image for display
			image_1_displayed = cv2.resize( self.image_1, None, fx=scale_factor, fy=scale_factor )
			image_2_displayed = cv2.resize( self.image_2, None, fx=scale_factor, fy=scale_factor )

			# Preview the calibration chessboard on the image
			if self.chessboard_enabled :

				image_1_displayed = Calibration.PreviewChessboard( image_1_displayed )
				image_2_displayed = Calibration.PreviewChessboard( image_2_displayed )

			# Prepare image for display
			stereo_image = np.concatenate( (image_1_displayed, image_2_displayed), axis=1 )
			
			# Display the image (scaled down)
			cv2.imshow( "Stereo Cameras", stereo_image )

			# Initialize image flags
			self.image_1_ready = False
			self.image_2_ready = False

			# Keyboard interruption
			key = cv2.waitKey( 10 ) & 0xFF
				
			# Escape key
			if key == 27 :
				
				# Exit live display
				self.capturing = False
				
			# Space key
			elif key == 32 :

				# Count images
				self.image_count += 1
				
				# Save image to disk 
				print( 'Save image {} to disk...'.format(self.image_count) )
				cv2.imwrite( 'camera-1-{:0>2}.png'.format(self.image_count), self.image_1 )
				cv2.imwrite( 'camera-2-{:0>2}.png'.format(self.image_count), self.image_2 )
				
			# C key
			elif key == ord('c') :
				
				# Enable / Disable chessboard preview
				self.chessboard_enabled = not self.chessboard_enabled		


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
		
		# Active live chessboard finding and drawing on the image
		self.chessboard_enabled = False
		
	#
	# Start capture and display image stream
	#
	def LiveDisplay( self ) :

		# Number of images saved
		image_count = 0
		
		# Image frames
		frame_1 = Vimba.VmbFrame( self.camera_1.payloadsize )
		frame_2 = Vimba.VmbFrame( self.camera_2.payloadsize )

		# Configure frame software trigger
		Vimba.vimba.VmbFeatureEnumSet( self.camera_1.handle, "TriggerSource", "Software" )
		Vimba.vimba.VmbFeatureEnumSet( self.camera_2.handle, "TriggerSource", "Software" )

		# Announce the frames
		Vimba.vimba.VmbFrameAnnounce( self.camera_1.handle, ct.byref(frame_1), ct.sizeof(frame_1) )
		Vimba.vimba.VmbFrameAnnounce( self.camera_2.handle, ct.byref(frame_2), ct.sizeof(frame_2) )

		# Start capture engine
		Vimba.vimba.VmbCaptureStart( self.camera_1.handle )
		Vimba.vimba.VmbCaptureStart( self.camera_2.handle )

		# Start acquisition
		Vimba.vimba.VmbFeatureCommandRun( self.camera_1.handle, "AcquisitionStart" )
		Vimba.vimba.VmbFeatureCommandRun( self.camera_2.handle, "AcquisitionStart" )

		# Live display
		while True :
			
			# Queue frames
			Vimba.vimba.VmbCaptureFrameQueue( self.camera_1.handle, ct.byref(frame_1), None )
			Vimba.vimba.VmbCaptureFrameQueue( self.camera_2.handle, ct.byref(frame_2), None )
			
			# Send software trigger
			Vimba.vimba.VmbFeatureCommandRun( self.camera_1.handle, "TriggerSoftware" )
			Vimba.vimba.VmbFeatureCommandRun( self.camera_2.handle, "TriggerSoftware" )

			# Get frames back
			Vimba.vimba.VmbCaptureFrameWait( self.camera_1.handle, ct.byref(frame_1), 1000 )
			Vimba.vimba.VmbCaptureFrameWait( self.camera_2.handle, ct.byref(frame_2), 1000 )
			
			# Check frame validity
			if frame_1.receiveStatus or frame_2.receiveStatus :
				continue
			
			# Convert frames to numpy arrays
			image_1 = np.fromstring( frame_1.buffer[ 0 : self.camera_1.payloadsize ], dtype=np.uint8 ).reshape( self.height, self.width )
			image_2 = np.fromstring( frame_2.buffer[ 0 : self.camera_2.payloadsize ], dtype=np.uint8 ).reshape( self.height, self.width )

			# Prepare image for display
			image_1_displayed = cv2.resize( image_1, None, fx=scale_factor, fy=scale_factor )
			image_2_displayed = cv2.resize( image_2, None, fx=scale_factor, fy=scale_factor )

			# Preview the calibration chessboard on the image
			if self.chessboard_enabled :

				image_1_displayed = Calibration.PreviewChessboard( image_1_displayed )
				image_2_displayed = Calibration.PreviewChessboard( image_2_displayed )

			# Prepare image for display
			stereo_image = np.concatenate( (image_1_displayed, image_2_displayed), axis=1 )
			
			# Display the image (scaled down)
			cv2.imshow( "Stereo Cameras", stereo_image )

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
				
			# C key
			elif key == ord('c') :
				
				# Enable / Disable chessboard preview
				self.chessboard_enabled = not self.chessboard_enabled		


		# Stop image acquisition
		self.camera_1.StopCapture()
		self.camera_2.StopCapture()
					
		# Cleanup OpenCV
		cv2.destroyAllWindows()
	
