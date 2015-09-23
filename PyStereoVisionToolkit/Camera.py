# -*- coding:utf-8 -*- 


#
# Module to display live images from two cameras
#


#
# External dependencies
#
import time
import cv2
import numpy as np
import Vimba


#
# Find the chessboard quickly, and draw it
#
def PreviewChessboard( image, pattern_size ) :
	
	# Find the chessboard corners on the image
	found, corners = cv2.findChessboardCorners( image, pattern_size, flags = cv2.CALIB_CB_FAST_CHECK )	
#	found, corners = cv2.findCirclesGridDefault( image, pattern_size, flags = cv2.CALIB_CB_ASYMMETRIC_GRID )	

	# Draw the chessboard corners on the image
	if found : cv2.drawChessboardCorners( image, pattern_size, corners, found )
		
	# Return the image with the chessboard if found
	return image


#
# Usb stereo camera viewer
#
def UsbStereoViewer( pattern_size ) :
		

	# Initialize the viewing parameters
	chessboard_enabled = False
	cross_enabled = False
	
	# Initialize the stereo cameras
	camera_left = cv2.VideoCapture( 0 )
	camera_right = cv2.VideoCapture( 1 )
	
	# Lower the camera frame rate
	camera_left.set( cv2.cv.CV_CAP_PROP_FPS, 5 )
	camera_right.set( cv2.cv.CV_CAP_PROP_FPS, 5 )

	# Live display
	while True :

		# Capture images
		camera_left.grab()
		camera_right.grab()

		# Get the images
		_, image_left = camera_left.retrieve()
		_, image_right = camera_right.retrieve()

		# Copy images for display
		image_left_displayed = np.array( image_left )
		image_right_displayed = np.array( image_right )

		# Preview the calibration chessboard on the image
		if chessboard_enabled :
			image_left_displayed = PreviewChessboard( image_left_displayed, pattern_size )
			image_right_displayed = PreviewChessboard( image_right_displayed, pattern_size )

		# Display a cross in the middle of the image
		if cross_enabled :
			w = image_left_displayed.shape[1]
			h = image_left_displayed.shape[0]
			w2 = int( w/2 )
			h2 = int( h/2 )
			cv2.line( image_left_displayed, (w2, 0), (w2, h), (0, 255, 0), 2 )
			cv2.line( image_left_displayed, (0, h2), (w, h2), (0, 255, 0), 2 )
			cv2.line( image_right_displayed, (w2, 0), (w2, h), (0, 255, 0), 2 )
			cv2.line( image_right_displayed, (0, h2), (w, h2), (0, 255, 0), 2 )

		# Prepare image for display
		stereo_image = np.concatenate( (image_left_displayed, image_right_displayed), axis=1 )
		
		# Display the image (scaled down)
		cv2.imshow( 'StereoVision', stereo_image )

		# Keyboard interruption
		key = cv2.waitKey( 1 ) & 0xFF
		
		# Escape key
		if key == 27 :
			
			# Exit live display
			break
			
		# Space key
		elif key == 32 :
			
			# Save images to disk 
			current_time = time.strftime( '%Y%m%d_%H%M%S' )
			print( 'Save images {} to disk...'.format(current_time) )
			cv2.imwrite( 'left-{}.png'.format(current_time), image_left )
			cv2.imwrite( 'right-{}.png'.format(current_time), image_right )
			
		# C key
		elif key == ord('c') :
			
			# Enable / Disable display of the middle cross
			cross_enabled = not cross_enabled		

		# M key
		elif key == ord('m') :
			
			# Enable / Disable chessboard preview
			chessboard_enabled = not chessboard_enabled		

	# Stop image acquisition
	camera_left.release()
	camera_right.release()
				
	# Cleanup OpenCV
	cv2.destroyAllWindows()


#
# Vimba stereo camera viewer
#
class VmbStereoViewer( object ) :
		
	#
	# Initialization
	#
	def __init__( self, pattern_size, scale_factor = 0.37 ) :
		
		# Initialize the viewing parameters
		chessboard_enabled = False
		cross_enabled = False
		zoom_enabled = False
		
		# Initialize the Vimba driver
		Vimba.VmbStartup()

		# Initialize the stereo cameras
		stereo_camera = Vimba.VmbStereoCamera( '50-0503326223', '50-0503323406' )

		# Connect the stereo cameras
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
			image_left = self.frame_left.image
			image_right = self.frame_right.image

			# Resize image for display
			image_left_displayed = cv2.resize( image_left, None, fx=scale_factor, fy=scale_factor )
			image_right_displayed = cv2.resize( image_right, None, fx=scale_factor, fy=scale_factor )
			
			# Convert grayscale image in color
			image_left_displayed = cv2.cvtColor( image_left_displayed, cv2.COLOR_GRAY2BGR )
			image_right_displayed = cv2.cvtColor( image_right_displayed, cv2.COLOR_GRAY2BGR )

			# Preview the calibration chessboard on the image
			if chessboard_enabled :
				image_left_displayed = PreviewChessboard( image_left_displayed, pattern_size )
				image_right_displayed = PreviewChessboard( image_right_displayed, pattern_size )

			# Zoom in the middle of the image
			if zoom_enabled :
				w = image_left.shape[1] / 2
				h = image_left.shape[0] / 2
				wd = image_left_displayed.shape[1] / 2
				hd = image_left_displayed.shape[0] / 2
				image_left_displayed[ hd-350:hd+350, wd-400:wd+400 ] = cv2.cvtColor( image_left[ h-350:h+350, w-400:w+400 ], cv2.COLOR_GRAY2BGR )
				image_right_displayed[ hd-350:hd+350, wd-400:wd+400 ] = cv2.cvtColor( image_right[ h-350:h+350, w-400:w+400 ], cv2.COLOR_GRAY2BGR )

			# Display a cross in the middle of the image
			if cross_enabled :
				w = image_left_displayed.shape[1]
				h = image_left_displayed.shape[0]
				w2 = int( w/2 )
				h2 = int( h/2 )
				cv2.line( image_left_displayed, (w2, 0), (w2, h), (0, 255, 0), 2 )
				cv2.line( image_left_displayed, (0, h2), (w, h2), (0, 255, 0), 2 )
				cv2.line( image_right_displayed, (w2, 0), (w2, h), (0, 255, 0), 2 )
				cv2.line( image_right_displayed, (0, h2), (w, h2), (0, 255, 0), 2 )

			# Prepare image for display
			stereo_image = np.concatenate( (image_left_displayed, image_right_displayed), axis=1 )
			
			# Display the image (scaled down)
			cv2.imshow( '{} - {}'.format( stereo_camera.camera_left.id, stereo_camera.camera_right.id ), stereo_image )

			# Keyboard interruption
			key = cv2.waitKey( 1 ) & 0xFF
			
			# Escape key
			if key == 27 :
				
				# Exit live display
				break
				
			# Space key
			elif key == 32 :
				
				# Save images to disk 
				current_time = time.strftime( '%Y%m%d_%H%M%S' )
				print( 'Save images {} to disk...'.format(current_time) )
				cv2.imwrite( 'left-{}.png'.format(current_time), image_left )
				cv2.imwrite( 'right-{}.png'.format(current_time), image_right )
				
			# C key
			elif key == ord('c') :
				
				# Enable / Disable chessboard preview
				chessboard_enabled = not chessboard_enabled		

			# M key
			elif key == ord('m') :
				
				# Enable / Disable display of the middle cross
				cross_enabled = not cross_enabled		

			# Z key
			elif key == ord('z') :
				
				# Enable / Disable zoom in the middle
				zoom_enabled = not zoom_enabled		

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
	def FrameCallback( self, frame_left, frame_right ) :

		# Save current frame
		self.frame_left = frame_left
		self.frame_right = frame_right

		# Frame ready
		self.frames_ready = True
