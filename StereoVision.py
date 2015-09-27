#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to calibrate stereo cameras, and to recontruct a 3D scene
#



#
# External dependencies
#
import os
import pickle
import time
import cv2
import numpy as np
import PyStereoVisionToolkit as psvtk


#
# Stereo disparity class
#
class StereoSGBM( object ) :
	
	#
	# Initialize the StereoSGBM, and display the disparity map
	#
	def __init__( self ) :
		
		# StereoSGBM parameters
		self.min_disparity = 16
		self.num_disp = 96
		self.sad_window_size = 3
		self.uniqueness = 10
		self.speckle_window_size = 100
		self.speckle_range = 2
		self.P1 = 216
		self.P2 = 864
		self.max_disparity = 1
		self.full_dp = False
		self.bm = cv2.StereoSGBM( minDisparity=self.min_disparity,
			numDisparities=self.num_disp,
			SADWindowSize=self.sad_window_size,
			uniquenessRatio=self.uniqueness,
			speckleWindowSize=self.speckle_window_size,
			speckleRange=self.speckle_range,
			disp12MaxDiff=self.max_disparity,
			P1=self.P1,
			P2=self.P2,
			fullDP=self.full_dp )

		# Display window
		cv2.namedWindow( 'SGBM' )
		cv2.createTrackbar( 'min_disparity', 'SGBM', self.min_disparity, 200, self.UpdateDisparity )
		cv2.createTrackbar( 'num_disp', 'SGBM', self.num_disp, 200, self.UpdateDisparity )
		cv2.createTrackbar( 'sad_window_size', 'SGBM', self.sad_window_size, 11, self.UpdateDisparity )
		cv2.createTrackbar( 'uniqueness', 'SGBM', self.uniqueness, 100, self.UpdateDisparity )
		cv2.createTrackbar( 'speckle_window_size', 'SGBM', self.speckle_window_size, 200, self.UpdateDisparity )
		cv2.createTrackbar( 'speckle_range', 'SGBM', self.speckle_range, 50, self.UpdateDisparity )
		cv2.createTrackbar( 'P1', 'SGBM', self.P1, 200, self.UpdateDisparity )
		cv2.createTrackbar( 'P2', 'SGBM', self.P2, 200, self.UpdateDisparity )
		cv2.createTrackbar( 'max_disparity', 'SGBM', self.max_disparity, 200, self.UpdateDisparity )
		
	#
	# Set the number ot disparities (multiple of 16)
	#
	def SetMinDisparity( self, value ) :
		if value % 16 :	value -= value % 16
		self.min_disparity = value
		cv2.setTrackbarPos( 'min_disparity', 'SGBM', self.min_disparity )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetNumDisp( self, value ) :
		if value % 16 :	value -= value % 16
		self.num_disp = value
		cv2.setTrackbarPos( 'num_disp', 'SGBM', self.num_disp )
		self.UpdateDisparity()

	#
	# Set the search window size (odd, and in range [1...11])
	#
	def SetSadWindowSize( self, value ) :
		if value < 1 : value = 1
		elif not value % 2 : value += 1
		self.SADWindowSize = value
		cv2.setTrackbarPos( 'SADWindowSize', 'SGBM', self.SADWindowSize )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetUniqueness( self, value ) :
		self.uniqueness = value
		cv2.setTrackbarPos( 'uniqueness', 'SGBM', self.uniqueness )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetSpeckleWindowSize( self, value ) :
		self.speckle_window_size = value
		cv2.setTrackbarPos( 'speckle_window_size', 'SGBM', self.speckle_window_size )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetSpeckleRange( self, value ) :
		self.speckle_range = value
		cv2.setTrackbarPos( 'speckle_range', 'SGBM', self.speckle_range )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetP1( self, value ) :
		self.P1 = value
		cv2.setTrackbarPos( 'P1', 'SGBM', self.P1 )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetP2( self, value ) :
		self.P2 = value
		cv2.setTrackbarPos( 'P2', 'SGBM', self.P2 )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetMaxDisparity( self, value ) :
		self.max_disparity = value
		cv2.setTrackbarPos( 'max_disparity', 'SGBM', self.max_disparity )
		self.UpdateDisparity()

	#
	# Compute the stereo correspondence
	#
	def UpdateDisparity( self ):
		
		self.bm = cv2.StereoSGBM( minDisparity=self.min_disparity,
			numDisparities=self.num_disp,
			SADWindowSize=self.sad_window_size,
			uniquenessRatio=self.uniqueness,
			speckleWindowSize=self.speckle_window_size,
			speckleRange=self.speckle_range,
			disp12MaxDiff=self.max_disparity,
			P1=self.P1,
			P2=self.P2,
			fullDP=self.full_dp )


	#
	# Compute the stereo correspondence
	#
	def ComputeDisparity( self, image_left, image_right ):

		self.bm_disparity = self.bm.compute( image_left, image_right )
		self.bm_disparity_img = self.bm_disparity.astype( np.float32 ) / 16.0
		cv2.normalize( self.bm_disparity_img, self.bm_disparity_img, 0, 255, cv2.NORM_MINMAX )
		self.bm_disparity_img = self.bm_disparity_img.astype( np.uint8 )
		image = cv2.applyColorMap( self.bm_disparity_img, cv2.COLORMAP_JET )
		cv2.imshow( 'SGBM', image )



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


# Create the directory for calibration files, if necessary
try : os.makedirs( 'Calibration' )
except OSError :
	if not os.path.isdir( 'Calibration' ) : raise
	
# Load the calibration parameter file, if it exists
calibration = None
if os.path.isfile( 'Calibration.pkl' ) :
	with open( 'Calibration.pkl' , 'rb') as calibration_file :
		calibration = pickle.load( calibration_file )

# Calibration pattern size
pattern_size = ( 9, 6 )

# The disparity object
disparity = StereoSGBM()

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
	key = cv2.waitKey( 10 ) & 0xFF
	
	# Escape key
	if key == 27 :
		
		# Exit live display
		break
		
	# Space key
	elif key == 32 :
		
		# Save images to disk 
		current_time = time.strftime( '%Y%m%d_%H%M%S' )
		print( 'Save images {} to disk...'.format(current_time) )
		# Calibration images
		if chessboard_enabled :
			cv2.imwrite( 'Calibration/left-{}.png'.format(current_time), image_left )
			cv2.imwrite( 'Calibration/right-{}.png'.format(current_time), image_right )
		# Regular images
		else :
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
		
	# P key
	elif key == ord('p') :
		
		# Calibrate the stereo cameras
		calibration = psvtk.Calibration.StereoCameraCalibration( 'Calibration', pattern_size )
		
	# R key
	elif key == ord('r') :
		
		# Remap the images according to the stereo camera calibration parameters
		image_left_remap = cv2.remap( image_left, calibration['left_map'][0], calibration['left_map'][1], cv2.INTER_LINEAR )
		image_right_remap = cv2.remap( image_right, calibration['right_map'][0], calibration['right_map'][1], cv2.INTER_LINEAR )
		
		disparity.ComputeDisparity( image_left_remap, image_right_remap )


# Stop image acquisition
camera_left.release()
camera_right.release()
			
# Cleanup OpenCV
cv2.destroyAllWindows()
