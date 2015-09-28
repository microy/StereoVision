# -*- coding:utf-8 -*- 


#
# Camera calibration module
#


#
# External dependencies
#
import glob
import math
import pickle
import cv2
import numpy as np


#
# Calibration pattern size
#
pattern_size = ( 9, 6 )

#
# Image scale factor for pattern detection
#
image_scale = 0.5



#
# Camera calibration
#
def CameraCalibration( image_files ) :
	
	# Chessboard pattern
	pattern_points = np.zeros( (np.prod(pattern_size), 3), np.float32 )
	pattern_points[:,:2] = np.indices(pattern_size).T.reshape(-1, 2)
	
	# Asymetric circles grid pattern
#	pattern_points = []
#	for i in xrange( pattern_size[1] ) :
#		for j in xrange( pattern_size[0] ) :
#			pattern_points.append( [ (2*j) + i%2 , i, 0 ] )
#	pattern_points = np.asarray( pattern_points, dtype=np.float32 )

	# Get image size
	height, width = cv2.imread( image_files[0] ).shape[:2]
#	img_size = tuple( cv2.pyrDown( cv2.imread( image_files[0] ), cv2.CV_LOAD_IMAGE_GRAYSCALE ).shape[:2] )
	img_size = ( width, height )
	
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
	#	image_small = cv2.pyrDown( image )
	#	image = image_small
		image_small = image

		# Chessboard detection flags
		flags  = 0
		flags |= cv2.CALIB_CB_ADAPTIVE_THRESH
		flags |= cv2.CALIB_CB_NORMALIZE_IMAGE

		# Find the chessboard corners on the image
		found, corners = cv2.findChessboardCorners( image_small, pattern_size, flags=flags )
	#	found, corners = cv2.findCirclesGridDefault( image, pattern_size, flags = cv2.CALIB_CB_ASYMMETRIC_GRID )	

		# Pattern not found
		if not found :
			print( 'Pattern not found on image {}...'.format( filename ) )
			continue
			
		# Rescale the corner position
	#	corners *= 1.0 / image_scale
	#	corners *= 2.0

		# Termination criteria
		criteria = ( cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 1e-5 )
	
		# Refine the corner positions
		cv2.cornerSubPix( image, corners, (11, 11), (-1, -1), criteria )
		
		# Store image and corner informations
		img_points.append( corners.reshape(-1, 2) )
		obj_points.append( pattern_points )
		img_files.append( filename )

	# Camera calibration flags
	flags  = 0
#	flags |= cv2.CALIB_USE_INTRINSIC_GUESS
#	flags |= cv2.CALIB_FIX_PRINCIPAL_POINT
#	flags |= cv2.CALIB_FIX_ASPECT_RATIO
#	flags |= cv2.CALIB_ZERO_TANGENT_DIST
#	flags |= cv2.CALIB_RATIONAL_MODEL
#	flags |= cv2.CALIB_FIX_K3
#	flags |= cv2.CALIB_FIX_K4
#	flags |= cv2.CALIB_FIX_K5

	# Camera calibration
	calibration = cv2.calibrateCamera( obj_points, img_points, img_size, flags=flags )
	
	# Store the calibration results in a dictionary
	parameter_names = ( 'calib_error', 'camera_matrix', 'dist_coefs', 'rvecs', 'tvecs' )
	calibration = dict( zip( parameter_names, calibration ) )
	
	# Compute reprojection error
	calibration['reproject_error'] = 0
	for i, obj in enumerate( obj_points ) :
		
		# Reproject the object points using the camera parameters
		reprojected_img_points, _ = cv2.projectPoints( obj, calibration['rvecs'][i],
		calibration['tvecs'][i], calibration['camera_matrix'], calibration['dist_coefs'] )
		
		# Compute the error with the original image points
		error = cv2.norm( img_points[i], reprojected_img_points.reshape(-1, 2), cv2.NORM_L2 )
		
		# Add to the total error
		calibration['reproject_error'] += error * error
		
	calibration['reproject_error'] = math.sqrt( calibration['reproject_error'] / (len(obj_points) * np.prod(pattern_size)) )
	
	# Print calibration results
	print( 'Calibration error : {}'.format( calibration['calib_error'] ) )
	print( 'Reprojection error : {}'.format( calibration['reproject_error'] ) )
	print( 'Camera matrix :\n{}'.format( calibration['camera_matrix'] ) )
	print( 'Distortion coefficients :\n{}'.format( calibration['dist_coefs'].ravel() ) )
	
	# Backup calibration parameters for future use
	calibration['img_points'] = img_points
	calibration['obj_points'] = obj_points
	calibration['img_size'] = img_size
	calibration['img_files'] = img_files
	calibration['pattern_size'] = pattern_size

	# Return the camera calibration results
	return calibration


#
# Stereo camera calibration
#
def StereoCameraCalibration() :

	# Calibrate the left camera
	print( '\n~~~ Left camera calibration ~~~\n' )
	cam1 = CameraCalibration( sorted( glob.glob( 'Calibration/left*.png' ) ) )
	
	# Calibrate the right camera
	print( '\n~~~ Right camera calibration ~~~\n' )
	cam2 = CameraCalibration( sorted( glob.glob( 'Calibration/right*.png' ) ) )

	# Calibrate the stereo cameras
	print( '\n~~~ Stereo camera calibration ~~~\n' )

	# Stereo calibration termination criteria
	criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)
	
	# Stereo calibration flags
	flags  = 0
	flags |= cv2.CALIB_USE_INTRINSIC_GUESS
#	flags |= cv2.CALIB_FIX_INTRINSIC
#	flags |= cv2.CALIB_FIX_PRINCIPAL_POINT
#	flags |= cv2.CALIB_FIX_FOCAL_LENGTH
	flags |= cv2.CALIB_FIX_ASPECT_RATIO
	flags |= cv2.CALIB_SAME_FOCAL_LENGTH
	flags |= cv2.CALIB_ZERO_TANGENT_DIST
#	flags |= cv2.CALIB_RATIONAL_MODEL
#	flags |= cv2.CALIB_FIX_K3
#	flags |= cv2.CALIB_FIX_K4
#	flags |= cv2.CALIB_FIX_K5

	# Stereo calibration
	calibration = cv2.stereoCalibrate( cam1['obj_points'], cam1['img_points'], cam2['img_points'],
		cam1['img_size'], cam1['camera_matrix'], cam1['dist_coefs'], cam2['camera_matrix'], cam2['dist_coefs'],
		flags=flags, criteria=criteria )
		
	# Store the stereo calibration results in a dictionary
	parameter_names = ( 'calib_error', 'camera_matrix_l', 'dist_coefs_l', 'camera_matrix_r', 'dist_coefs_r', 'R', 'T', 'E', 'F' )
	calibration = dict( zip( parameter_names, calibration ) )
	
	# Stereo rectification
	rectification = cv2.stereoRectify(
		calibration['camera_matrix_l'], calibration['dist_coefs_l'],
		calibration['camera_matrix_r'], calibration['dist_coefs_r'],
		cam1['img_size'], calibration['R'], calibration['T'], flags=0 )
		
	# Store the stereo rectification results in the dictionary
	parameter_names = ( 'R1', 'R2', 'P1', 'P2', 'Q', 'ROI1', 'ROI2' )
	calibration.update( zip( parameter_names, rectification ) )

	# Undistortion maps
	calibration['left_map'] = cv2.initUndistortRectifyMap(
		calibration['camera_matrix_l'], calibration['dist_coefs_l'],
		calibration['R1'], calibration['P1'], cam1['img_size'], cv2.CV_32FC1 )
	calibration['right_map'] = cv2.initUndistortRectifyMap(
		calibration['camera_matrix_r'], calibration['dist_coefs_r'],
		calibration['R2'], calibration['P2'], cam2['img_size'], cv2.CV_32FC1 )

	# Compute reprojection error
	undistorted_l = cv2.undistortPoints( np.concatenate( cam1['img_points'] ).reshape(-1, 1, 2),
		calibration['camera_matrix_l'], calibration['dist_coefs_l'], P=calibration['camera_matrix_l'] )
	undistorted_r = cv2.undistortPoints( np.concatenate( cam2['img_points'] ).reshape(-1, 1, 2),
		calibration['camera_matrix_r'], calibration['dist_coefs_r'], P=calibration['camera_matrix_r'] )
	lines_l = cv2.computeCorrespondEpilines( undistorted_l, 1, calibration['F'] )
	lines_r = cv2.computeCorrespondEpilines( undistorted_r, 2, calibration['F'] )
	calibration['reproject_error'] = 0
	for i in range( len( undistorted_l ) ) :
		calibration['reproject_error'] += abs( undistorted_l[i][0][0] * lines_r[i][0][0] +
			undistorted_l[i][0][1] * lines_r[i][0][1] + lines_r[i][0][2] ) + abs( undistorted_r[i][0][0] * lines_l[i][0][0] +
			undistorted_r[i][0][1] * lines_l[i][0][1] + lines_l[i][0][2] )
	calibration['reproject_error'] /= len( undistorted_r )

	# Print calibration results
	print( 'Stereo calibration error : {}'.format( calibration['calib_error'] ) )
	print( 'Reprojection error : {}'.format( calibration['reproject_error'] ) )
	print( 'Left camera matrix :\n{}'.format( calibration['camera_matrix_l'] ) )
	print( 'Left distortion coefficients :\n{}'.format( calibration['dist_coefs_l'].ravel() ) )
	print( 'Right camera matrix :\n{}'.format( calibration['camera_matrix_r'] ) )
	print( 'Right distortion coefficients :\n{}'.format( calibration['dist_coefs_r'].ravel() ) )
	print( 'Rotation matrix :\n{}'.format( calibration['R'] ) )
	print( 'Translation vector :\n{}'.format( calibration['T'].ravel() ) )
	print( 'Essential matrix :\n{}'.format( calibration['E'] ) )
	print( 'Fundamental matrix :\n{}'.format( calibration['F'] ) )
	print( 'Rotation matrix for the first camera :\n{}'.format( calibration['R1'] ) )
	print( 'Rotation matrix for the second camera :\n{}'.format( calibration['R2'] ) )
	print( 'Projection matrix for the first camera :\n{}'.format( calibration['P1'] ) )
	print( 'Projection matrix for the second camera :\n{}'.format( calibration['P2'] ) )
	print( 'Disparity-to-depth mapping matrix :\n{}'.format( calibration['Q'] ) )
	print( 'ROI for the left camera :  {}'.format( calibration['ROI1'] ) )
	print( 'ROI for the right camera : {}\n'.format( calibration['ROI2'] ) )
	
	# Write the results
	with open( 'Calibration/calibration.pkl' , 'wb') as output_file :
		pickle.dump( calibration, output_file, pickle.HIGHEST_PROTOCOL )
		
	return calibration
