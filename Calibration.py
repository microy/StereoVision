# -*- coding:utf-8 -*- 


#
# Camera calibration module
#


#
# External dependencies
#
import json
import os
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
# JSON encoder for Numpy arrays
#
class NumpyEncoder( json.JSONEncoder ) :
	
	# Overload the defaut JSON encoder
    def default( self, obj ) :
		
		# Encoder for Numpy arrays
		if isinstance( obj, np.ndarray ) :
			
			# Array of dimension = 1
			if obj.ndim == 1 : return obj.tolist()

			# Array of dimension > 1
			else : return [ self.default( obj[i] ) for i in range( obj.shape[0] ) ]

		# Default encoder
		return json.JSONEncoder.default( self, obj )


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
	img_size = cv2.imread( image_files[0], cv2.CV_LOAD_IMAGE_GRAYSCALE ).shape[:2]
	
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
		image_small = cv2.resize( image, None, fx=image_scale, fy=image_scale )

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
		corners /= image_scale

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
	if debug :
		print( "RMS : {}".format( calibration['rms'] ) )
		print( "Camera matrix :\n{}".format( calibration['camera_matrix'] ) )
		print( "Distortion coefficients :\n{}".format( calibration['dist_coefs'].ravel() ) )
	
	# Write calibration results in a JSON file
	if output :
		with open( output , 'w') as output_file :
			json.dump( calibration, output_file, cls=NumpyEncoder )

	return calibration

#
# Stereo camera calibration
#
def StereoCameraCalibration( debug = False ) :

	# Read camera calibration files
	with open( 'camera-left.json' , 'r') as calibfile :
		cam1 = json.load( calibfile )
	with open( 'camera-right.json' , 'r') as calibfile :
		cam2 = json.load( calibfile )
		
	# Convert camera calibration data into Numpy arrays
	for key in [ 'img_points', 'obj_points', 'camera_matrix', 'dist_coefs' ] :
		cam1[ key ] = np.asarray( cam1[ key ], dtype=np.float32 )
		cam2[ key ] = np.asarray( cam2[ key ], dtype=np.float32 )
	
	# Get image size
	img_size = tuple( cam1['img_size'] )
	
#	criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)
#	criteria = ( cv2.TERM_CRITERIA_COUNT + cv2.TERM_CRITERIA_EPS, 30, 1e-6 )
#	flags = 0
#	flags |= cv2.CALIB_FIX_ASPECT_RATIO
#	flags |= cv2.CALIB_ZERO_TANGENT_DIST
#	flags |= cv2.CALIB_SAME_FOCAL_LENGTH
#	flags |= cv2.CALIB_RATIONAL_MODEL
#	flags |= cv2.CALIB_FIX_K3
#	flags |= cv2.CALIB_FIX_K4
#	flags |= cv2.CALIB_FIX_K5

	print( 'Stereo-calibration...' )

	# Stereo calibration
	stereo_calibration = cv2.stereoCalibrate( cam1['obj_points'], cam1['img_points'], cam2['img_points'], img_size )
	parameter_names = ( 'rms_stereo', 'camera_matrix_l', 'dist_coeffs_l', 'camera_matrix_r', 'dist_coeffs_r', 'R', 'T', 'E', 'F' )
	stereo_calibration = dict( zip( parameter_names, stereo_calibration ) )

	# Print calibration results
	if debug : print( "Stereo RMS : {}".format( stereo_calibration['rms_stereo'] ) )

	print( 'Stereo-rectification...' )

	# Stereo rectification
	stereo_rectify = cv2.stereoRectify( cam1['camera_matrix'], cam1['dist_coefs'], cam2['camera_matrix'], cam2['dist_coefs'], img_size, stereo_calibration['R'], stereo_calibration['T'] )
	parameter_names = ( 'R1', 'R2', 'P1', 'P2', 'Q', 'ROI1', 'ROI2' )
	stereo_rectify = dict( zip( parameter_names, stereo_rectify ) )
	

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

	print( 'Undistord images...' )
	left_maps = cv2.initUndistortRectifyMap(
		stereo_calibration['camera_matrix_l'],
		stereo_calibration['dist_coeffs_l'],
		stereo_rectify['R1'], stereo_rectify['P1'],
		img_size, cv2.CV_16SC2 )

	right_maps = cv2.initUndistortRectifyMap(
		stereo_calibration['camera_matrix_r'],
		stereo_calibration['dist_coeffs_r'],
		stereo_rectify['R2'], stereo_rectify['P2'],
		img_size, cv2.CV_16SC2 )

	left_image = cv2.remap( left_image, left_maps[0], left_maps[1], cv2.INTER_LINEAR )
	right_image = cv2.remap( right_image, right_maps[0], right_maps[1], cv2.INTER_LINEAR )

#	cv2.imshow('left', cv2.pyrDown(left_image))
#	cv2.imshow('right', cv2.pyrDown(right_image))
	cv2.imshow('BM disparity', cv2.pyrDown(bm_disparity))
	cv2.imshow('SGBM disparity', cv2.pyrDown(sgbm_disparity))
	cv2.waitKey()
	cv2.destroyAllWindows()
