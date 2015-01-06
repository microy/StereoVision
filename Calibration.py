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
	
