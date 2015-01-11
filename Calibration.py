# -*- coding:utf-8 -*- 


#
# Camera calibration module
#


#
# External dependencies
#
import cv2


#
# Find the chessboard and draw it
#
def PreviewChessboard( image, pattern_size = ( 9, 6 ), scale = 0.5 ) :
	
	# Resize image
	preview = cv2.resize( image, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST )

	# Find the chessboard corners on the image
	found_all, corners = cv2.findChessboardCorners( preview, pattern_size, flags = cv2.CALIB_CB_FAST_CHECK )
		
	# Chessboard found
	if found_all :
		
		# Convert grayscale image in color
		preview = cv2.cvtColor( preview, cv2.COLOR_GRAY2BGR )

		# Draw the chessboard corners on the image
		cv2.drawChessboardCorners( preview, pattern_size, corners, found_all )
	
	# Chessboard found or not
	return preview



def TestCalibration() :

	# External dependencies
	import numpy as np
	import glob
	import sys

	# Get image file names
	image_files = glob.glob( sys.argv[1] )

	# Chessboard pattern
	pattern_size = ( 9, 6 )
#	pattern_points = np.zeros( (np.prod(pattern_size), 3), np.float32 )
#	pattern_points[:,:2] = np.indices(pattern_size).T.reshape(-1, 2)

	# Termination criteria
	term = ( cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1 )
	
	# Scale factor for corner detection
	scale = 0.5

#	obj_points = []
#	img_points = []
#	h, w = 0, 0

	# For each image
	for filename in image_files :
		
		# Load the image
		image = cv2.imread( filename, cv2.CV_LOAD_IMAGE_GRAYSCALE )

		# image sharpening
#		image_blur = cv2.GaussianBlur( image, (0,0), 105)
#		image = cv2.addWeighted( image, 1.8, image_blur, -0.8, 0 )
			
#		h, w = image.shape[:2]

		# Preview chessboard on image
		preview = PreviewChessboard( image, pattern_size, scale )
		cv2.imshow( "Chessboard", preview )
		cv2.waitKey()
		
		# Resize image
		image_small = cv2.resize( image, None, fx=scale, fy=scale )

		# Find the chessboard corners on the image
		found_all, corners = cv2.findChessboardCorners( image_small, pattern_size, None , cv2.cv.CV_CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_FILTER_QUADS )
		
		# Chessboard found
		if found_all :
			
			# Store image and corner informations
#			img_points.append( corners.reshape(-1, 2) )
#			obj_points.append( pattern_points )

			corners /= scale
			
			# Refine the corner position
#			cv2.cornerSubPix( image, corners, (11, 11), (-1, -1), term )

			# Draw the chessboard corners on the image
			image_color = cv2.cvtColor( image, cv2.COLOR_GRAY2BGR )
			cv2.drawChessboardCorners( image_color, pattern_size, corners, found_all )
			
			# Resize image for display
			image_color = cv2.resize( image_color, None, fx=0.3, fy=0.3 )

			# Display the image with the found corners
			cv2.imshow( "Chessboard", image_color )
			cv2.waitKey()
		
		# No chessboard found
		else : print( "Chessboard no found..." )


	# Camera calibration
#	rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera( obj_points, img_points, (w, h), None, None )
#	print "RMS:", rms
#	print "Camera matrix:\n", camera_matrix
#	print "Distortion coefficients:\n", dist_coefs.ravel()


	# Cleanup OpenCV windows
	cv2.destroyAllWindows()
