# -*- coding:utf-8 -*- 


#
# Camera calibration module
#


#
# External dependencies
#
import cv2


#
# Chessboard pattern dimensions
#
pattern_size = ( 13, 10 )


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
def TestCalibration( imagefile_name ) :

	# External dependencies
	import numpy as np
	import glob
	import sys

	# Get image file names
	image_files = glob.glob( imagefile_name )

	# Chessboard pattern
	pattern_points = np.zeros( (np.prod(pattern_size), 3), np.float32 )
	pattern_points[:,:2] = np.indices(pattern_size).T.reshape(-1, 2)

	# Termination criteria
	term = ( cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1 )
	
	# Scale factor for corner detection
	scale = 0.35
	
	# Pattern type
	pattern_type = "Chessboard"

	# 3D points
	obj_points = []
	
	# 2D points
	img_points = []
	
	# Image size
	height, width = 0, 0
	
	# For each image
	for filename in image_files :
		
		# Load the image
		image = cv2.imread( filename, cv2.CV_LOAD_IMAGE_GRAYSCALE )

		# Get image size
		height, width = image.shape[:2]

		# Resize image
		image_small = cv2.resize( image, None, fx=scale, fy=scale )

		# Preview chessboard on image
		preview = PreviewChessboard( image_small )
		
		# Find the chessboard corners on the image
		found_all, corners = cv2.findChessboardCorners( image_small, pattern_size, None , cv2.cv.CV_CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_FILTER_QUADS )
		
		# Chessboard found
		if found_all :
			
			# Rescale the corner position
			corners /= scale
			
			# Refine the corner position
			cv2.cornerSubPix( image, corners, (11, 11), (-1, -1), term )

			# Store image and corner informations
			img_points.append( corners.reshape(-1, 2) )
			obj_points.append( pattern_points )

			# Draw the chessboard corners on the image
			image_color = cv2.cvtColor( image, cv2.COLOR_GRAY2BGR )
			cv2.drawChessboardCorners( image_color, pattern_size, corners, found_all )
			
			# Resize image for display
			image_color = cv2.resize( image_color, None, fx=0.3, fy=0.3 )

			# Display the image with the found corners
			cv2.imshow( "Chessboard", image_color )
			cv2.waitKey()
		
		# No chessboard found
		else : print( "Chessboard no found on image {}...".format(filename) )

	# Camera calibration
	rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera( obj_points, img_points, (width, height), None, None )
	print "RMS:", rms
	print "Camera matrix:\n", camera_matrix
	print "Distortion coefficients:\n", dist_coefs.ravel()

	# Reprojection error
#	mean_error = 0
#	for i in xrange(len(obj_points)):
#		imgpoints2, _ = cv2.projectPoints(obj_points[i], rvecs[i], tvecs[i], camera_matrix, dist_coefs)
#		print( img_points[i].shape, imgpoints2.shape )
#		error = cv2.norm(img_points[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
#		mean_error += error
#	print "total error: ", mean_error/len(obj_points)

	# Cleanup OpenCV windows
	cv2.destroyAllWindows()

