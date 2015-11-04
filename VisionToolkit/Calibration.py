# -*- coding:utf-8 -*-


#
# Camera calibration module
#


#
# External dependencies
#
import glob
import math
import os
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
# Calibration directory setup
#
calibration_directory = 'Calibration'


#
# Create the calibration directory
#
def CreateCalibrationDirectory() :
	try : os.makedirs( calibration_directory )
	except OSError :
		if not os.path.isdir( calibration_directory ) : raise


#
# Load the calibration parameters from a file
#
def LoadCalibration( filename = 'calibration.pkl' ) :
	calibration = None
	if os.path.isfile( '{}/{}'.format( calibration_directory, filename ) ) :
		with open( '{}/{}'.format( calibration_directory, filename ) , 'rb' ) as calibration_file :
			calibration = pickle.load( calibration_file )
	return calibration


#
# Save the calibration parameters to a file
#
def SaveCalibration( calibration, filename = 'calibration.pkl' ) :

	# Write the calibration object with all the parameters
	with open( '{}/{}'.format( calibration_directory, filename ) , 'wb') as calibration_file :
		pickle.dump( calibration, calibration_file, pickle.HIGHEST_PROTOCOL )


#
# Find the chessboard quickly, and draw it
#
def PreviewChessboard( image ) :

	# Find the chessboard corners on the image
	found, corners = cv2.findChessboardCorners( image, pattern_size, flags = cv2.CALIB_CB_FAST_CHECK )
#	found, corners = cv2.findCirclesGridDefault( image, pattern_size, flags = cv2.CALIB_CB_ASYMMETRIC_GRID )

	# Draw the chessboard corners on the image
	if found : cv2.drawChessboardCorners( image, pattern_size, corners, found )

	# Return the image with the chessboard if found
	return image


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
	flags |= cv2.CALIB_RATIONAL_MODEL
#	flags |= cv2.CALIB_FIX_K3
	flags |= cv2.CALIB_FIX_K4
	flags |= cv2.CALIB_FIX_K5

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
	cam1 = CameraCalibration( sorted( glob.glob( '{}/left*.png'.format(calibration_directory) ) ) )

	# Calibrate the right camera
	cam2 = CameraCalibration( sorted( glob.glob( '{}/right*.png'.format(calibration_directory) ) ) )

	# Stereo calibration termination criteria
	criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)

	# Stereo calibration flags
	flags  = 0
	flags |= cv2.CALIB_USE_INTRINSIC_GUESS
#	flags |= cv2.CALIB_FIX_INTRINSIC
#	flags |= cv2.CALIB_FIX_PRINCIPAL_POINT
#	flags |= cv2.CALIB_FIX_FOCAL_LENGTH
	flags |= cv2.CALIB_FIX_ASPECT_RATIO
#	flags |= cv2.CALIB_SAME_FOCAL_LENGTH
#	flags |= cv2.CALIB_ZERO_TANGENT_DIST
	flags |= cv2.CALIB_RATIONAL_MODEL
	flags |= cv2.CALIB_FIX_K3
	flags |= cv2.CALIB_FIX_K4
	flags |= cv2.CALIB_FIX_K5

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

	# Write calibration results
	with open( '{}/calibration.log'.format(calibration_directory) , 'w') as output_file :
		output_file.write( '\n~~~ Left camera calibration ~~~\n\n' )
		output_file.write( 'Calibration error : {}\n'.format( cam1['calib_error'] ) )
		output_file.write( 'Reprojection error : {}\n'.format( cam1['reproject_error'] ) )
		output_file.write( 'Camera matrix :\n{}\n'.format( cam1['camera_matrix'] ) )
		output_file.write( 'Distortion coefficients :\n{}\n'.format( cam1['dist_coefs'].ravel() ) )
		output_file.write( '\n~~~ Right camera calibration ~~~\n\n' )
		output_file.write( 'Calibration error : {}\n'.format( cam2['calib_error'] ) )
		output_file.write( 'Reprojection error : {}\n'.format( cam2['reproject_error'] ) )
		output_file.write( 'Camera matrix :\n{}\n'.format( cam2['camera_matrix'] ) )
		output_file.write( 'Distortion coefficients :\n{}\n'.format( cam2['dist_coefs'].ravel() ) )
		output_file.write( '\n~~~ Stereo camera calibration ~~~\n\n' )
		output_file.write( 'Stereo calibration error : {}\n'.format( calibration['calib_error'] ) )
		output_file.write( 'Reprojection error : {}\n'.format( calibration['reproject_error'] ) )
		output_file.write( 'Left camera matrix :\n{}\n'.format( calibration['camera_matrix_l'] ) )
		output_file.write( 'Left distortion coefficients :\n{}\n'.format( calibration['dist_coefs_l'].ravel() ) )
		output_file.write( 'Right camera matrix :\n{}\n'.format( calibration['camera_matrix_r'] ) )
		output_file.write( 'Right distortion coefficients :\n{}\n'.format( calibration['dist_coefs_r'].ravel() ) )
		output_file.write( 'Rotation matrix :\n{}\n'.format( calibration['R'] ) )
		output_file.write( 'Translation vector :\n{}\n'.format( calibration['T'].ravel() ) )
		output_file.write( 'Essential matrix :\n{}\n'.format( calibration['E'] ) )
		output_file.write( 'Fundamental matrix :\n{}\n'.format( calibration['F'] ) )
		output_file.write( 'Rotation matrix for the first camera :\n{}\n'.format( calibration['R1'] ) )
		output_file.write( 'Rotation matrix for the second camera :\n{}\n'.format( calibration['R2'] ) )
		output_file.write( 'Projection matrix for the first camera :\n{}\n'.format( calibration['P1'] ) )
		output_file.write( 'Projection matrix for the second camera :\n{}\n'.format( calibration['P2'] ) )
		output_file.write( 'Disparity-to-depth mapping matrix :\n{}\n'.format( calibration['Q'] ) )
		output_file.write( 'ROI for the left camera :  {}\n'.format( calibration['ROI1'] ) )
		output_file.write( 'ROI for the right camera : {}\n'.format( calibration['ROI2'] ) )

	# Write the calibration object with all the parameters
	with open( '{}/calibration.pkl'.format(calibration_directory) , 'wb') as output_file :
		pickle.dump( calibration, output_file, pickle.HIGHEST_PROTOCOL )

	# Return the calibration
	return calibration


#
# Stereo image undistortion
#
def StereoRectification( calibration, left_image, right_image, display = False ) :

	# Remap the images
	left_image = cv2.remap( left_image, calibration['left_map'][0], calibration['left_map'][1], cv2.INTER_LINEAR )
	right_image = cv2.remap( right_image, calibration['right_map'][0], calibration['right_map'][1], cv2.INTER_LINEAR )

	# Display the rectified images
	if display :

		# Print ROI
		cv2.rectangle( left_image, calibration['ROI1'][:2], calibration['ROI1'][2:], (0,0,255), 2 )
		cv2.rectangle( right_image, calibration['ROI2'][:2], calibration['ROI2'][2:], (0,0,255), 2 )

		# Print lines
		for i in range( 0, left_image.shape[0], 32 ) :
			cv2.line( left_image, (0, i), (left_image.shape[1], i), (0, 255, 0), 2 )
			cv2.line( right_image, (0, i), (right_image.shape[1], i), (0, 255, 0), 2 )

	# Return the rectified images
	return left_image, right_image
