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
import Calibration
import Vimba
from PySide import QtCore
from PySide import QtGui


class QtCameraViewer( QtGui.QLabel ) :

	#
	# Initialisation
	#
	def __init__( self, parent = None, calibration = None ) :

		# Initialise QLabel
		super( QtCameraViewer, self ).__init__( parent )

		# Store the calibration parameters
		self.calibration = calibration

		# Initialize the widget parameters
		self.setAlignment( QtCore.Qt.AlignCenter )
		self.setFixedSize( 1280, 480 )

		# Initialize the viewing parameters
		self.chessboard_enabled = False
		self.cross_enabled = False
		self.disparity_enabled = False

		# StereoBM parameters
	#	self.bm = cv2.StereoBM( cv2.STEREO_BM_BASIC_PRESET, 64, 5 )
		self.bm = cv2.StereoSGBM( 16, 96, 5 )
		
		# Initialize the stereo cameras
		self.camera_left = cv2.VideoCapture( 0 )
		self.camera_right = cv2.VideoCapture( 1 )

		# Lower the camera frame rate
		self.camera_left.set( cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640 )
		self.camera_left.set( cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480 )
		self.camera_right.set( cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640 )
		self.camera_right.set( cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480 )
		self.camera_left.set( cv2.cv.CV_CAP_PROP_FPS, 5 )
		self.camera_right.set( cv2.cv.CV_CAP_PROP_FPS, 5 )

		# Timer for capture
		self.timer = QtCore.QTimer( self )
		self.timer.timeout.connect( self.QueryFrame )
		self.timer.start( 1000 / 5 )

	#
	# Capture frames and display them
	#
	def QueryFrame( self ) :
		
		# Capture images
		self.camera_left.grab()
		self.camera_right.grab()

		# Get the images
		_, self.image_left = self.camera_left.retrieve()
		_, self.image_right = self.camera_right.retrieve()

		# Copy images for display
		image_left_displayed = np.array( self.image_left )
		image_right_displayed = np.array( self.image_right )

		# Preview the calibration chessboard on the image
		if self.chessboard_enabled :
			image_left_displayed = Calibration.PreviewChessboard( image_left_displayed )
			image_right_displayed = Calibration.PreviewChessboard( image_right_displayed )

		# Display a cross in the middle of the image
		if self.cross_enabled :
			w = image_left_displayed.shape[1]
			h = image_left_displayed.shape[0]
			w2 = int( w/2 )
			h2 = int( h/2 )
			cv2.line( image_left_displayed, (w2, 0), (w2, h), (0, 255, 0), 2 )
			cv2.line( image_left_displayed, (0, h2), (w, h2), (0, 255, 0), 2 )
			cv2.line( image_right_displayed, (w2, 0), (w2, h), (0, 255, 0), 2 )
			cv2.line( image_right_displayed, (0, h2), (w, h2), (0, 255, 0), 2 )

		# Display the disparity image
		if self.disparity_enabled and self.calibration :
			
			# Undistort the images according to the stereo camera calibration parameters
			rectified_images = Calibration.StereoRectification( self.calibration, self.image_left, self.image_right, True )
			rectified_images = cv2.pyrDown( rectified_images[0] ), cv2.pyrDown( rectified_images[1] )
		
			self.disparity = self.bm.compute( *rectified_images )
			disparity_image = self.disparity.astype( np.float32 ) / 16.0
			cv2.normalize( disparity_image, disparity_image, 0, 255, cv2.NORM_MINMAX )
		
		#	rectified_images = cv2.cvtColor( rectified_images[0], cv2.COLOR_BGR2GRAY ), cv2.cvtColor( rectified_images[1], cv2.COLOR_BGR2GRAY )
		#	self.disparity = self.bm.compute( *rectified_images, disptype=cv2.CV_32F )
		#	disparity_image = self.disparity * 255.99 / ( self.disparity.max() - self.disparity.min() )

			disparity_image = disparity_image.astype( np.uint8 )
#			disparity_image = cv2.applyColorMap( disparity_image, cv2.COLORMAP_JET )
			disparity_image = cv2.cvtColor( disparity_image, cv2.COLOR_GRAY2RGB )
		#	disparity_image = cv2.pyrUp( disparity_image )
			stereo_image = disparity_image
		
		# Or display the stereo images
		else :
			
			# Prepare image for display
			stereo_image = np.concatenate( (image_left_displayed, image_right_displayed), axis=1 )
			stereo_image = cv2.cvtColor( stereo_image, cv2.COLOR_BGR2RGB )
		
		# Set the image
		self.setPixmap( QtGui.QPixmap.fromImage( QtGui.QImage( stereo_image,
			stereo_image.shape[1], stereo_image.shape[0], QtGui.QImage.Format_RGB888 ) ) )
			
		# Update the widget
		self.update()
		
	#
	# Close the camera viewer
	#
	def closeEvent( self, event ) :
		
		# Stop image acquisition
		self.timer.stop()
		self.camera_left.release()
		self.camera_right.release()
		event.accept()


#
# Usb stereo camera viewer
#
def UsbStereoViewer() :
	
	# Load the calibration parameter file, if it exists
	import os, pickle
	calibration = None
	if os.path.isfile( '{}/calibration.pkl'.format(Calibration.calibration_directory) ) :
		with open( '{}/calibration.pkl'.format(Calibration.calibration_directory) , 'rb') as calibration_file :
			calibration = pickle.load( calibration_file )

	# StereoBM parameters
	bm = cv2.StereoSGBM( 16, 96, 5 )

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
			image_left_displayed = Calibration.PreviewChessboard( image_left_displayed )
			image_right_displayed = Calibration.PreviewChessboard( image_right_displayed )

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


		# Undistort the images according to the stereo camera calibration parameters
		rectified_images = Calibration.StereoRectification( calibration, image_left, image_right )
		rectified_images = cv2.pyrDown( rectified_images[0] ), cv2.pyrDown( rectified_images[1] )
		pr_bm_disparity = bm.compute( *rectified_images )
		pr_bm_disparity_img = pr_bm_disparity.astype( np.float32 ) / 16.0
		cv2.normalize( pr_bm_disparity_img, pr_bm_disparity_img, 0, 255, cv2.NORM_MINMAX )
		pr_bm_disparity_img = pr_bm_disparity_img.astype( np.uint8 )
		pr_bm_disparity_img = cv2.applyColorMap( pr_bm_disparity_img, cv2.COLORMAP_JET )
		cv2.imshow( 'Disparity preview', pr_bm_disparity_img )

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
			if chessboard_enabled :
				cv2.imwrite( '{}/left-{}.png'.format(Calibration.calibration_directory, current_time), image_left )
				cv2.imwrite( '{}/right-{}.png'.format(Calibration.calibration_directory, current_time), image_right )
			else :
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
			
		# P key
		elif key == ord('p') :
			
			# Calibrate the stereo cameras
			calibration = Calibration.StereoCameraCalibration()

		# R key
		elif key == ord('r') :
			
			# Undistort the images according to the stereo camera calibration parameters
			rectified_images = Calibration.StereoRectification( calibration, image_left, image_right )
			bm_disparity = bm.compute( *rectified_images )
			bm_disparity_img = bm_disparity.astype( np.float32 ) / 16.0
			cv2.normalize( bm_disparity_img, bm_disparity_img, 0, 255, cv2.NORM_MINMAX )
			bm_disparity_img = bm_disparity_img.astype( np.uint8 )
			bm_disparity_img = cv2.applyColorMap( bm_disparity_img, cv2.COLORMAP_JET )
			cv2.imshow( 'Disparity', bm_disparity_img )


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
