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
def FindAndDrawChessboard( image, pattern_size = ( 9, 6 ) ) :
	
	# Find the chessboard corners on the image
	found_all, corners = cv2.findChessboardCorners( image, pattern_size )
	
	# Chessboard found
	if found_all :
		
		# Convert grayscale image in color
		image = cv2.cvtColor( image, cv2.COLOR_GRAY2BGR )

		# Draw the chessboard corners on the image
		cv2.drawChessboardCorners( image, pattern_size, corners, found_all )
	

def TestCalibration() :

	# External dependencies
	import numpy as np
	import glob
	import sys

	# Get image file names
	image_files = glob.glob( sys.argv[1] )

	# Chessboard pattern
	pattern_size = ( 9, 6 )
	pattern_points = np.zeros( (np.prod(pattern_size), 3), np.float32 )
	pattern_points[:,:2] = np.indices(pattern_size).T.reshape(-1, 2)

	# Termination criteria
	term = ( cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1 )

	obj_points = []
	img_points = []
	h, w = 0, 0

	# For each image
	for filename in image_files :
		
		# Load the image
		image = cv2.imread( filename, cv2.CV_LOAD_IMAGE_GRAYSCALE )
			
		# Resize image for display
		image = cv2.resize( image, None, fx=0.3, fy=0.3 )

		h, w = image.shape[:2]
		
		# Find the chessboard corners on the image
		found_all, corners = cv2.findChessboardCorners( image, pattern_size )
		
		# Chessboard found
		if found_all :
			
			# Refine the corner position
#			cv2.cornerSubPix( image, corners, (11, 11), (-1, -1), term )

			# Store image and corner informations
#			img_points.append( corners.reshape(-1, 2) )
#			obj_points.append( pattern_points )
			
			# Draw the chessboard corners on the image
			image_color = cv2.cvtColor( image, cv2.COLOR_GRAY2BGR )
			cv2.drawChessboardCorners( image_color, pattern_size, corners, found_all )
			
			# Display the image with the found corners
			cv2.imshow( "Chessboard", image_color )
			cv2.waitKey()
		
		# No chessboard found
		else :
			
			print( "Chessboard no found..." )


	# Camera calibration
#	rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera( obj_points, img_points, (w, h), None, None )
#	print "RMS:", rms
#	print "Camera matrix:\n", camera_matrix
#	print "Distortion coefficients:\n", dist_coefs.ravel()


	# Cleanup OpenCV windows
	cv2.destroyAllWindows()
