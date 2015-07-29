# -*- coding:utf-8 -*- 


#
# Camera calibration module
#


#
# External dependencies
#
import os
import pickle
import sys
import cv2
import numpy as np


#
# Calibration parameters
#

# Pattern type
pattern_size = ( 15, 10 )

# Image scale factor for pattern detection
image_scale = 0.35


#
# Find the chessboard quickly and draw it
#
def PreviewChessboard( image ) :
	
	# Convert grayscale image in color
	image = cv2.cvtColor( image, cv2.COLOR_GRAY2BGR )

	# Find the chessboard corners on the image
	found_all, corners = cv2.findChessboardCorners( image, pattern_size, flags = cv2.CALIB_CB_FAST_CHECK )	

	# Chessboard found
	if found_all :
		
		# Draw the chessboard corners on the image
		cv2.drawChessboardCorners( image, pattern_size, corners, found_all )
		
	return image


#
# Camera calibration
#
def CameraCalibration( image_files, output = None, debug = False ) :
	
	# Chessboard pattern
	pattern_points = np.zeros( (np.prod(pattern_size), 3), np.float32 )
	pattern_points[:,:2] = np.indices(pattern_size).T.reshape(-1, 2)

	# Get image size
	img_size = tuple( cv2.pyrDown( cv2.imread( image_files[0] ), cv2.CV_LOAD_IMAGE_GRAYSCALE ).shape[:2] )
	
	# 3D points
	obj_points = []
	
	# 2D points
	img_points = []
	
	# Images with chessboard found
	img_files = []
	
	# For each image
	for filename in image_files :
		
		# Load the image
		image = cv2.imread( filename, cv2.CV_LOAD_IMAGE_GRAYSCALE )

		# Resize image
	#	image_small = cv2.resize( image, None, fx=image_scale, fy=image_scale )
		image_small = cv2.pyrDown( image )
		image = image_small

		# Chessboard detection flags
		flags = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE

		# Find the chessboard corners on the image
		found_all, corners = cv2.findChessboardCorners( image_small, pattern_size, flags=flags )

		# Pattern not found
		if not found_all :
			
			print( "Pattern not found on image {}...".format(filename) )
			continue
			
		# Preview chessboard on image
		if debug :
			
			# Convert grayscale image in color
			image_color = cv2.cvtColor( image_small, cv2.COLOR_GRAY2BGR )
			
			# Draw the chessboard corners on the image
			cv2.drawChessboardCorners( image_color, pattern_size, corners, found_all )
			
			# Display the image with the chessboard
			cv2.imshow( filename, image_color )
			
			# Wait for a key
			cv2.waitKey()

			# Cleanup OpenCV window
			cv2.destroyWindow( filename )
		
		# Rescale the corner position
	#	corners /= image_scale
	#	corners *= 2.0

		# Termination criteria
		criteria = ( cv2.TERM_CRITERIA_COUNT + cv2.TERM_CRITERIA_EPS, 30, sys.float_info.epsilon )
	
		# Refine the corner positions
		cv2.cornerSubPix( image, corners, (11, 11), (-1, -1), criteria )
		
		# Store image and corner informations
		img_points.append( corners.reshape(-1, 2) )
		obj_points.append( pattern_points )
		img_files.append( filename )

	# Camera calibration
	calibration = cv2.calibrateCamera( obj_points, img_points, img_size )
	parameter_names = ( 'rms', 'camera_matrix', 'dist_coefs', 'rvecs', 'tvecs' )
	calibration = dict( zip( parameter_names, calibration ) )
	
	# Backup image and object points
	calibration['img_points'] = img_points
	calibration['obj_points'] = obj_points

	# Backup image size and filenames
	calibration['img_size'] = img_size
	calibration['img_files'] = img_files

	# Print calibration results
	print( "RMS : {}".format( calibration['rms'] ) )
	print( "Camera matrix :\n{}".format( calibration['camera_matrix'] ) )
	print( "Distortion coefficients :\n{}".format( calibration['dist_coefs'].ravel() ) )
	
	# Write calibration results with pickle
	if output :
		with open( 'camera-{}.pkl'.format( output ) , 'wb') as output_file :
			pickle.dump( calibration, output_file, pickle.HIGHEST_PROTOCOL )

	return calibration

#
# Stereo camera calibration
#
def StereoCameraCalibration( debug = False ) :

	# Read camera calibration files
	with open( 'camera-left.pkl' , 'rb') as calibfile :
		cam1 = pickle.load( calibfile )
	with open( 'camera-right.pkl' , 'rb') as calibfile :
		cam2 = pickle.load( calibfile )
		
#	criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)
	criteria = ( cv2.TERM_CRITERIA_COUNT + cv2.TERM_CRITERIA_EPS, 30, 1e-6 )
	flags = 0
#	flags |= cv2.CALIB_FIX_ASPECT_RATIO
#	flags |= cv2.CALIB_ZERO_TANGENT_DIST
#	flags |= cv2.CALIB_SAME_FOCAL_LENGTH
#	flags |= cv2.CALIB_RATIONAL_MODEL
#	flags |= cv2.CALIB_FIX_K3
#	flags |= cv2.CALIB_FIX_K4
#	flags |= cv2.CALIB_FIX_K5

	print( 'Stereo calibration...' )

	# Stereo calibration
	stereo_calibration = cv2.stereoCalibrate( cam1['obj_points'], cam1['img_points'], cam2['img_points'], cam1['img_size'], flags=flags, criteria=criteria )
	parameter_names = ( 'rms_stereo', 'camera_matrix_l', 'dist_coefs_l', 'camera_matrix_r', 'dist_coefs_r', 'R', 'T', 'E', 'F' )
	stereo_calibration = dict( zip( parameter_names, stereo_calibration ) )

	# Print calibration results
	print( "RMS : {}".format( stereo_calibration['rms_stereo'] ) )
	print( "Left camera matrix :\n{}".format( stereo_calibration['camera_matrix_l'] ) )
	print( "Left distortion coefficients :\n{}".format( stereo_calibration['dist_coefs_l'].ravel() ) )
	print( "Right camera matrix :\n{}".format( stereo_calibration['camera_matrix_r'] ) )
	print( "Right distortion coefficients :\n{}".format( stereo_calibration['dist_coefs_r'].ravel() ) )

	print( 'Stereo rectification...' )

	# Stereo rectification
	stereo_rectify = cv2.stereoRectify( cam1['camera_matrix'], cam1['dist_coefs'], cam2['camera_matrix'], cam2['dist_coefs'], cam1['img_size'], stereo_calibration['R'], stereo_calibration['T'] )
	parameter_names = ( 'R1', 'R2', 'P1', 'P2', 'Q', 'ROI1', 'ROI2' )
	stereo_rectify = dict( zip( parameter_names, stereo_rectify ) )
	
	# Write results with pickle
	with open( 'stereo-calibration.pkl' , 'wb') as output_file :
		pickle.dump( stereo_calibration, output_file, pickle.HIGHEST_PROTOCOL )
	with open( 'stereo-rectification.pkl' , 'wb') as output_file :
		pickle.dump( stereo_rectify, output_file, pickle.HIGHEST_PROTOCOL )


#
# Undistort images
#
def UndistortImages() :

	print( 'Undistort images...' )
	left_image = cv2.pyrDown( cv2.imread( cam1['img_files'][0], cv2.CV_LOAD_IMAGE_GRAYSCALE ) )
	right_image = cv2.pyrDown( cv2.imread( cam2['img_files'][0], cv2.CV_LOAD_IMAGE_GRAYSCALE ) )
	
	left_maps = cv2.initUndistortRectifyMap(
		cam1['camera_matrix'],
		cam1['dist_coefs'],
		stereo_rectify['R1'], stereo_rectify['P1'],
		cam1['img_size'], cv2.CV_16SC2 )

	right_maps = cv2.initUndistortRectifyMap(
		cam2['camera_matrix'],
		cam2['dist_coefs'],
		stereo_rectify['R2'], stereo_rectify['P2'],
		cam2['img_size'], cv2.CV_16SC2 )

	left_image = cv2.remap( left_image, left_maps[0], left_maps[1], cv2.INTER_LINEAR )
	right_image = cv2.remap( right_image, right_maps[0], right_maps[1], cv2.INTER_LINEAR )
	
	left_image = cv2.rectangle( left_image, (384,0),(510,128),(0,255,0),3 )

	cv2.imshow('left', left_image )
	cv2.imshow('right', right_image )
	cv2.waitKey()
	cv2.destroyAllWindows()


#
# Stereo disparity
#
def Disparity() :

	left_image = cv2.imread( cam1['img_files'][0], cv2.CV_LOAD_IMAGE_GRAYSCALE )
	right_image = cv2.imread( cam2['img_files'][0], cv2.CV_LOAD_IMAGE_GRAYSCALE )


	print( 'Computing BM disparity...' )

	bm = cv2.StereoBM( cv2.STEREO_BM_BASIC_PRESET, 48, 9)
	bm_disparity = bm.compute( left_image, right_image, disptype=cv2.CV_16S )
	bm_disparity *= 255 / ( bm_disparity.min() - bm_disparity.max() )
	bm_disparity = bm_disparity.astype( np.uint8 )


	print( 'Computing SGBM disparity...' )

	# disparity range
	min_disparity = 0
	num_disparities = 64
	sad_window_size = 3
	p1 = 216
	p2 = 864
	disp12_max_diff = 1
	prefilter_cap = 63
	uniqueness_ratio = 10
	speckle_window_size = 100
	speckle_range = 32
	full_dp = False
	
	sgbm = cv2.StereoSGBM( min_disparity, num_disparities, sad_window_size, p1, p2, disp12_max_diff,
		prefilter_cap, uniqueness_ratio, speckle_window_size, speckle_range, full_dp )

	sgbm_disparity = sgbm.compute( left_image, right_image )
	sgbm_disparity *= 255 / ( sgbm_disparity.min() - sgbm_disparity.max() )
	sgbm_disparity = sgbm_disparity.astype( np.uint8 )

	cv2.imshow('BM disparity', cv2.pyrDown(bm_disparity))
	cv2.imshow('SGBM disparity', cv2.pyrDown(sgbm_disparity))
	cv2.waitKey()
	cv2.destroyAllWindows()
