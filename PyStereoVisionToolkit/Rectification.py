# -*- coding:utf-8 -*- 


#
# Image rectification module
#


#
# External dependencies
#
import glob
import pickle
import cv2
import numpy as np


#
# Image rectification
#
def StereoRectification( image_directory ) :

	# Load stereo calibration parameter file
	with open( 'stereo-calibration.pkl' , 'rb') as calibration_file :
		calibration = pickle.load( calibration_file )
	
	# Get image list
	left_image_files = sorted( glob.glob( '{}/left*.png'.format( image_directory ) ) )
	right_image_files = sorted( glob.glob( '{}/right*.png'.format( image_directory ) ) )
		
	# Loop through the images
	for i in range( len( left_image_files ) ) :
		
		# Read the images
		left_image = cv2.imread( left_image_files[i] )
		right_image = cv2.imread( right_image_files[i] )

		# Remap the images according to the stereo camera calibration parameters
		left_image = cv2.remap( left_image, calibration['left_map'][0], calibration['left_map'][1], cv2.INTER_LINEAR )
		right_image = cv2.remap( right_image, calibration['right_map'][0], calibration['right_map'][1], cv2.INTER_LINEAR )
		
		# Write the rectified images
		cv2.imwrite( left_image_files[i].replace( '.png', '_rectified.png' ), left_image )
		cv2.imwrite( right_image_files[i].replace( '.png', '_rectified.png' ), right_image )



#
# Undistort images according to the camera calibration parameters
#
def UndistortImages( calibration ) :
	
	# Optimize the camera matrix
	new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
		calibration['camera_matrix'], calibration['dist_coefs'], calibration['img_size'], 1 )
	
	# Compute distortion rectification map
	rectify_map = cv2.initUndistortRectifyMap( calibration['camera_matrix'],
		calibration['dist_coefs'], None, new_camera_matrix, calibration['img_size'], cv2.CV_32FC1 )
		
	# Undistort calibration images
	for i, filename in enumerate( calibration['img_files'] ) :
		
		# Load the image
		image = cv2.imread( filename, cv2.CV_LOAD_IMAGE_GRAYSCALE )

		# Undistort the image
		undistorted_image = cv2.remap( image, rectify_map[0], rectify_map[1], cv2.INTER_LINEAR )

		# Convert grayscale images to color
		image = cv2.cvtColor( image, cv2.COLOR_GRAY2BGR )
		undistorted_image = cv2.cvtColor( undistorted_image, cv2.COLOR_GRAY2BGR )

		# Print ROI
		cv2.rectangle( undistorted_image, roi[:2], roi[2:], (0,0,255), 3 )
		
		# Display the original and the undistorted images
		preview = cv2.pyrDown( np.concatenate( (image, undistorted_image), axis=1 ) )
		cv2.imshow( 'Original - Undistorted' , preview )
		cv2.waitKey( 700 )
	
	# Close the chessboard preview windows
	cv2.destroyAllWindows()


#
# Stereo image undistortion
#
def StereoUndistortImages( cam1, cam2, calibration ) :
	
	# Display undistorted calibration images
	for i in range( len( cam1['img_files'] ) )  :
		
		# Load the image
		left_image = cv2.imread( cam1['img_files'][i], cv2.CV_LOAD_IMAGE_GRAYSCALE )
		right_image = cv2.imread( cam2['img_files'][i], cv2.CV_LOAD_IMAGE_GRAYSCALE )

		# Remap the images
		left_image = cv2.remap( left_image, calibration['left_map'][0], calibration['left_map'][1], cv2.INTER_LINEAR )
		right_image = cv2.remap( right_image, calibration['right_map'][0], calibration['right_map'][1], cv2.INTER_LINEAR )
	
		# Convert grayscale images to color
		left_image = cv2.cvtColor( left_image, cv2.COLOR_GRAY2BGR )
		right_image = cv2.cvtColor( right_image, cv2.COLOR_GRAY2BGR )

		# Print ROI
		cv2.rectangle( left_image, calibration['ROI1'][:2], calibration['ROI1'][2:], (0,0,255), 2 )
		cv2.rectangle( right_image, calibration['ROI2'][:2], calibration['ROI2'][2:], (0,0,255), 2 )
		
		# Prepare image for display
		undist_images = np.concatenate( (left_image, right_image), axis=1 )
		
		# Print lines
		for i in range( 0, undist_images.shape[0], 32 ) :
			cv2.line( undist_images, (0, i), (undist_images.shape[1], i), (0, 255, 0), 2 )

		# Show the result
		cv2.imshow('Undistorted stereo images', cv2.pyrDown( undist_images ) )
		cv2.waitKey()

	# Close preview window
	cv2.destroyAllWindows()

