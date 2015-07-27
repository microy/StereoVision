# -*- coding:utf-8 -*- 


#
# Module to display live images from two AVT cameras
#


#
# External dependencies
#
import cv2
import numpy as np
import Calibration
import Vimba


#
# Vimba stereo camera viewer
#
class VmbStereoViewer( object ) :
		
	#
	# Initialization
	#
	def __init__( self, scale_factor = 0.37 ) :

		# Initialize Vimba
		Vimba.VmbStartup()

		# The cameras
		stereo_camera = Vimba.VmbStereoCamera( '50-0503323406', '50-0503326223' )

		# Number of image saved
		image_count = 0

		# Active live chessboard finding and drawing on the image
		chessboard_enabled = False
		
		# Open the cameras
		stereo_camera.Open()

		# Start image acquisition
		stereo_camera.StartCapture( self.FrameCallback )

		# Live display
		while True :

			# Initialize frame status
			self.frames_ready = False

			# Wait for the frames
			while not self.frames_ready : pass

			# Convert the frames to images
			image_1 = self.frame_1.image
			image_2 = self.frame_2.image

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
			cv2.imshow( "{} - {}".format( stereo_camera.camera_1.id, stereo_camera.camera_2.id ), stereo_image )

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
				cv2.imwrite( 'left{:0>2}.png'.format(image_count), image_1 )
				cv2.imwrite( 'right{:0>2}.png'.format(image_count), image_2 )
				
			# C key
			elif key == ord('c') :
				
				# Enable / Disable chessboard preview
				chessboard_enabled = not chessboard_enabled		

		# Stop image acquisition
		stereo_camera.StopCapture()
					
		# Cleanup OpenCV
		cv2.destroyAllWindows()
	
		# Close the cameras
		stereo_camera.Close()

		# Shutdown Vimba
		Vimba.VmbShutdown()

	#
	# Receive the frames from both cameras
	#
	def FrameCallback( self, frame_1, frame_2 ) :

		# Save current frame
		self.frame_1 = frame_1
		self.frame_2 = frame_2

		# Frame ready
		self.frames_ready = True
