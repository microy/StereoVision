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

		# Vimba initialization
		Vimba.VmbStartup()

		# The cameras
		self.stereo_camera = Vimba.VmbStereoCamera( '50-0503323406', '50-0503326223' )

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

			# Capture the frames
			frame_1, frame_2 = self.stereo_camera.CaptureFrames()
			
			# Check the frames
			if not ( frame_1.is_valid and frame_2.is_valid ) :
				print( 'Invalid frames...' )
				continue

			# Convert the frames to images
			image_1 = frame_1.image
			image_2 = frame_2.image

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
			cv2.imshow( "{} - {}".format( self.stereo_camera.camera_1.id, self.stereo_camera.camera_2.id ), stereo_image )

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
				cv2.imwrite( 'camera-{}-{:0>2}.png'.format(self.stereo_camera.camera_1.id, image_count), image_1 )
				cv2.imwrite( 'camera-{}-{:0>2}.png'.format(self.stereo_camera.camera_2.id, image_count), image_2 )
				
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

		# Vimba shutdown
		Vimba.VmbShutdown()
