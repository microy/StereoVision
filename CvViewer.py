# -*- coding:utf-8 -*- 


#
# Module to display live images from AVT cameras
#


#
# External dependencies
#
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
class VmbViewer( object ) :
	
	#
	# Initialization
	#
	def __init__( self, camera_id ) :
		
		# The camera
		self.camera = Vimba.VmbCamera( self.camera_id )
		
	#
	# Start capture and display image stream
	#
	def LiveDisplay( self ) :

		# Number of image saved
		image_count = 0

		# Active live chessboard finding and drawing on the image
		chessboard_enabled = False

		# Initialize frame status
		self.frame_ready = False

		# Open the camera
		self.camera.Open()
		
		# Start image acquisition
		self.camera.StartCapture( self.FrameCallback )
		
		# Streaming loop
		while True :
			
			# Wait for a frame
			while not self.frame_ready : pass

			# Retreive the camera image
			image = self.frame.GetImage()
			
			# Resize image for display
			image_displayed = cv2.resize( image, None, fx=scale_factor, fy=scale_factor )

			# Preview the calibration chessboard on the image
			if chessboard_enabled :
				image_displayed = Calibration.PreviewChessboard( image_displayed )
			
			# Display the image (scaled down)
			cv2.imshow( self.camera.id_string, image_displayed )
			
			# Keyboard interruption
			key = cv2.waitKey( 1 ) & 0xFF
				
			# Escape key
			if key == 27 :
				
				# Exit the streaming loop
				break
				
			# Space key
			elif key == 32 :
				
				# Save image to disk 
				image_count += 1
				print( 'Save image {} to disk...'.format(image_count) )
				cv2.imwrite( 'camera-{}-{:0>2}.png'.format(self.camera.id_string, image_count), image )
				
			# C key
			elif key == ord('c') :
				
				# Enable / Disable chessboard preview
				chessboard_enabled = not chessboard_enabled
				
			# Initialize frame status
			self.frame_ready = False

		# Stop image acquisition
		self.camera.StopCapture()

		# Cleanup OpenCV
		cv2.destroyAllWindows()
		
		# Close the camera
		self.camera.Close()

	#
	# Receive a frame from the camera
	#
	def FrameCallback( self, frame ) :
		
		# Save current frame
		self.frame = frame
		
		# Frame ready
		self.frame_ready = True


#
# Vimba stereo camera viewer
#
class VmbStereoViewer( object ) :
		
	#
	# Initialization
	#
	def __init__( self, camera_1_id, camera_2_id ) :

		# The cameras
		self.stereo_camera = Vimba.VmbStereoCamera( self.camera_1_id, self.camera_2_id )

	#
	# Start capture and display image stream
	#
	def LiveDisplay( self ) :

		# Number of image saved
		image_count = 0

		# Active live chessboard finding and drawing on the image
		chessboard_enabled = False
		
		# Open the cameras
		self.stereo_camera.Open()

		# Start image acquisition
		self.stereo_camera.StartCapture()

		# Live display
		while True :

			# Capture images
			image_1, image_2 = self.stereo_camera.CaptureFrames()
			
			# Prepare image for display
			image_1_displayed = cv2.resize( image_1, None, fx=scale_factor, fy=scale_factor )
			image_2_displayed = cv2.resize( image_2, None, fx=scale_factor, fy=scale_factor )

			# Preview the calibration chessboard on the image
			if chessboard_enabled :

				image_1_displayed = Calibration.PreviewChessboard( image_1_displayed )
				image_2_displayed = Calibration.PreviewChessboard( image_2_displayed )

			# Prepare image for display
			stereo_image = np.concatenate( (image_1_displayed, image_2_displayed), axis=1 )
			
			# Display the image (scaled down)
			cv2.imshow( "{} - {}".format( self.camera_1_id, self.camera_2_id ), stereo_image )

			# Keyboard interruption
			key = cv2.waitKey( 1 ) & 0xFF
			
			# Escape key
			if key == 27 :
				
				# Exit live display
				break
				
			# Space key
			elif key == 32 :
				
				# Save images to disk 
				image_count += 1
				print( 'Save images {} to disk...'.format(image_count) )
				cv2.imwrite( 'camera-{}-{:0>2}.png'.format(self.camera_1_id, image_count), image_1 )
				cv2.imwrite( 'camera-{}-{:0>2}.png'.format(self.camera_2_id, image_count), image_2 )
				
			# C key
			elif key == ord('c') :
				
				# Enable / Disable chessboard preview
				chessboard_enabled = not chessboard_enabled		

		# Stop image acquisition
		self.stereo_camera.StopCapture()
					
		# Cleanup OpenCV
		cv2.destroyAllWindows()
	
		# Close the cameras
		self.stereo_camera.Close()
