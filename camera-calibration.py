#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to calibrate a camera
#


#
# External dependencies
#
import cv2
import numpy
import glob


#
# Find the chessboard
#


# Termination criteria
criteria = ( cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001 )

# Prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = numpy.zeros( (6*7, 3), np.float32 )
objp[ :, :2 ] = numpy.mgrid[ 0:7, 0:6 ].T.reshape( -1, 2 )

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

# Find image files
image_files = glob.glob( '*.png' )

# For each image files
for file_name in image_files:

	# Read the image file
    image = cv2.imread( file_name )

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners( image, (7,6), None )

    # If found, add object points, image points (after refining them)
    if ret == True :
		
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix( image, corners, (11,11), (-1,-1), criteria )
        imgpoints.append( corners2 )

        # Draw and display the corners
        image = cv2.drawChessboardCorners( image, (7,6), corners2, ret )
        cv2.imshow( 'Chessboard', image )
        cv2.waitKey( 0 )

cv2.destroyAllWindows()
