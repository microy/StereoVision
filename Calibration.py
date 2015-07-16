# -*- coding:utf-8 -*- 


#
# Camera calibration module
#


#
# External dependencies
#
import glob
import sys
import cv2
import numpy as np


#
# Calibration pattern parameters
#

# Pattern type
pattern_size = ( 15, 10 )
pattern_type = 'Chessboard'

# Image scale factor for pattern detection
image_scale = 0.35


#
# Class to calibrate a camera
#
class CameraCalibration( object ) :
	
	#
	# Member variables
	#
	
	# Pattern type
	pattern_size = ( 15, 10 )
	pattern_type = 'Chessboard'

	# Image scale factor for pattern detection
	image_scale = 0.35
	

	#
	# Camera calibration
	#
	def Calibrate( imagefile_name, debug = False ) :

		# Get image file names
		image_files = glob.glob( imagefile_name )

		# Chessboard pattern
		pattern_points = np.zeros( (np.prod(pattern_size), 3), np.float32 )
		pattern_points[:,:2] = np.indices(pattern_size).T.reshape(-1, 2)

		# Image size
		height, width = 0, 0

		# 3D points
		obj_points = []

		# 2D points
		img_points = []

		# For each image
		for filename in image_files :
			
			# Load the image
			image = cv2.imread( filename, cv2.CV_LOAD_IMAGE_GRAYSCALE )

			# Get image size
			height, width = image.shape[:2]

			# Resize image
			image_small = cv2.resize( image, None, fx=image_scale, fy=image_scale )

			# Chessboard pattern
			if pattern_type == 'Chessboard' :
				
				# Chessboard detection flags
				flags = cv2.cv.CV_CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FILTER_QUADS

				# Find the chessboard corners on the image
				found_all, corners = cv2.findChessboardCorners( image_small, pattern_size )

			# Asymetric circles grid pattern
			else :
			
				# Circles grid detection flags
				flags = cv2.CALIB_CB_ASYMMETRIC_GRID
				
				# Find the circles grid on the image
				found_all, corners = cv2.findCirclesGridDefault( image_small, pattern_size, None, flags )
			
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

			# Refine chessboard corner positions
			if pattern_type == 'Chessboard' :

				# Termination criteria
				term = ( cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 0.01 )

				# Refine the corner positions
				cv2.cornerSubPix( image, corners, (11, 11), (-1, -1), term )
			
			# Store image and corner informations
			img_points.append( corners.reshape(-1, 2) )
			obj_points.append( pattern_points )

		# Camera calibration
		parameter_names = ( 'rms', 'camera_matrix', 'dist_coefs', 'rvecs', 'tvecs' )
		calibration = dict( zip( parameter_names, cv2.calibrateCamera( obj_points, img_points, (width, height), None, None ) ) )

		print( "RMS : {}".format( calibration['rms'] ) )
		print( "Camera matrix :\n{}".format( calibration['camera_matrix'] ) )
		print( "Distortion coefficients :\n{}".format( calibration['dist_coefs'].ravel() ) )

		return calibration, img_points, obj_points




#
# Find the chessboard quickly and draw it
#
def PreviewChessboard( image ) :
	
	# Convert grayscale image in color
	image = cv2.cvtColor( image, cv2.COLOR_GRAY2BGR )

	# Chessboard pattern
	if pattern_type == 'Chessboard' :
		
		# Find the chessboard corners on the image
		found_all, corners = cv2.findChessboardCorners( image, pattern_size, flags = cv2.CALIB_CB_FAST_CHECK )	

	# Asymetric circle grid pattern
	else :
		
		# Find the circle grid on the image
		found_all, corners = cv2.findCirclesGridDefault( image, pattern_size, None, cv2.CALIB_CB_ASYMMETRIC_GRID )
		
	# Chessboard found
	if found_all :
		
		# Draw the chessboard corners on the image
		cv2.drawChessboardCorners( image, pattern_size, corners, found_all )
		
	return image


#
# Camera calibration
#
def CameraCalibration( imagefile_name, debug = False ) :
	
	# Get image file names
	image_files = glob.glob( imagefile_name )

	# Chessboard pattern
	pattern_points = np.zeros( (np.prod(pattern_size), 3), np.float32 )
	pattern_points[:,:2] = np.indices(pattern_size).T.reshape(-1, 2)

	# Image size
	height, width = 0, 0
	
	# 3D points
	obj_points = []
	
	# 2D points
	img_points = []
	
	# For each image
	for filename in image_files :
		
		# Load the image
		image = cv2.imread( filename, cv2.CV_LOAD_IMAGE_GRAYSCALE )

		# Get image size
		height, width = image.shape[:2]

		# Resize image
		image_small = cv2.resize( image, None, fx=image_scale, fy=image_scale )

		# Chessboard pattern
		if pattern_type == 'Chessboard' :
			
			# Chessboard detection flags
			flags = cv2.cv.CV_CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FILTER_QUADS

			# Find the chessboard corners on the image
			found_all, corners = cv2.findChessboardCorners( image_small, pattern_size )

		# Asymetric circles grid pattern
		else :
		
			# Circles grid detection flags
			flags = cv2.CALIB_CB_ASYMMETRIC_GRID
			
			# Find the circles grid on the image
			found_all, corners = cv2.findCirclesGridDefault( image_small, pattern_size, None, flags )
		
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

		# Refine chessboard corner positions
		if pattern_type == 'Chessboard' :

			# Termination criteria
			term = ( cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 0.01 )
	
			# Refine the corner positions
			cv2.cornerSubPix( image, corners, (11, 11), (-1, -1), term )
		
		# Store image and corner informations
		img_points.append( corners.reshape(-1, 2) )
		obj_points.append( pattern_points )

	# Camera calibration
	parameter_names = ( 'rms', 'camera_matrix', 'dist_coefs', 'rvecs', 'tvecs' )
	calibration = dict( zip( parameter_names, cv2.calibrateCamera( obj_points, img_points, (width, height), None, None ) ) )

	print( "RMS : {}".format( calibration['rms'] ) )
	print( "Camera matrix :\n{}".format( calibration['camera_matrix'] ) )
	print( "Distortion coefficients :\n{}".format( calibration['dist_coefs'].ravel() ) )

	return calibration, img_points, obj_points


#
# Stereo camera calibration
#
def StereoCameraCalibration( left_image_files, right_image_files, debug = False ) :

	# Get image file names
	image_files = np.array( zip( sorted(glob.glob( left_image_files )), sorted(glob.glob( right_image_files )) ) )
	
	# Load the image
	image = cv2.imread( image_files[0,0], cv2.CV_LOAD_IMAGE_GRAYSCALE )

	# Get image size
	height, width = image.shape[:2]
	print( height, width )
	print( image_files[0,:] )

#	calibration1, img_points1, obj_points1 = CameraCalibration( left_image_files )
#	calibration2, img_points2, obj_points2 = CameraCalibration( right_image_files )
	
#	criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)
#	flags = (cv2.CALIB_FIX_ASPECT_RATIO + cv2.CALIB_ZERO_TANGENT_DIST + cv2.CALIB_SAME_FOCAL_LENGTH)
	
#	stereo_calibration = cv2.stereoCalibrate(obj_points1, img_points1, img_points2, (width, height), criteria=criteria, flags=flags)[1:]
#	print( stereo_calibration )
#	stereo_rectify = cv2.stereoRectify(calib.cam_mats["left"], calib.dist_coefs["left"], calib.cam_mats["right"], calib.dist_coefs["right"], self.image_size, calib.rot_mat, calib.trans_vec, flags=0)


#	(error, left_intrinsics, left_distortion, right_intrinsics, right_distorition, R, T, E, F) = cv2.stereoCalibrate( obj_points1, img_points1, img_points2, (width, height), criteria=criteria, flags=flags)
#	print( error )

#	R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify( left_intrinsics, left_distortion, right_intrinsics, right_distortion, (width, height), R, T, alpha=0 )
	
	
	bm = cv2.StereoBM( cv2.STEREO_BM_BASIC_PRESET, 48, 9)
	left_image = cv2.imread( image_files[0,0], cv2.CV_LOAD_IMAGE_GRAYSCALE )
	right_image = cv2.imread( image_files[0,1], cv2.CV_LOAD_IMAGE_GRAYSCALE )
	disparity = bm.compute( left_image, right_image, disptype=cv2.CV_16S)
	disparity *= 255 / (disparity.min() - disparity.max())
	disparity = disparity.astype(np.uint8)
	cv2.imshow( "disparity", cv2.resize( disparity, None, fx=image_scale, fy=image_scale ) )
	cv2.waitKey()

