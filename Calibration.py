# -*- coding:utf-8 -*- 


#
# Camera calibration module
#


#
# External dependencies
#
import math
import cv2
import numpy as np


#
# Image scale factor for pattern detection
#
image_scale = 0.5



#
# Camera calibration
#
def CameraCalibration( image_files, pattern_size, debug = False ) :
	
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
	height, width = cv2.imread( image_files[0], cv2.CV_LOAD_IMAGE_GRAYSCALE ).shape[:2]
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

		# Preview chessboard on image
		if debug :
			
			# Convert grayscale image in color
			image_color = cv2.cvtColor( image_small, cv2.COLOR_GRAY2BGR )
			
			# Draw the chessboard corners on the image
			cv2.drawChessboardCorners( image_color, pattern_size, corners, found )
			
			# Display the image with the chessboard
			cv2.imshow( filename, cv2.pyrDown( image_color ) )
			cv2.waitKey( 700 )
			cv2.destroyWindow( filename )

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
# Stereo camera calibration
#
def StereoCameraCalibration( cam1, cam2, debug = False ) :

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

	# This is replaced because my results were always bad. Estimates are
	# taken from the OpenCV samples.
#	width, height = cam1['img_size']
#	focal_length = 0.8 * width
#	calibration['Q'] = np.float32( [[1, 0, 0, -0.5 * width],
#			[0, -1, 0, 0.5 * height],
#			[0, 0, 0, -focal_length],
#			[0, 0, 1, 0]] )

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
	print( 'ROI for the left camera :\n{}'.format( calibration['ROI1'] ) )
	print( 'ROI for the right camera :\n{}'.format( calibration['ROI2'] ) )
	
	# Return the camera calibration results
	return calibration


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


#
# Class to export 3D point cloud
#
class PointCloud( object ) :

	#
    # Header for exporting point cloud to PLY file format
    #
    ply_header = (
'''ply
format ascii 1.0
element vertex {vertex_count}
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
''')

	#
	# Initialize the point cloud
	#
    def __init__( self, coordinates, colors ) :
		self.coordinates = coordinates.reshape(-1, 3)
		self.colors = colors.reshape(-1, 3)

	#
	# Export the point cloud to a PLY file
	#
    def WritePly( self, output_file ) :
		mask = self.coordinates[:, 2] > self.coordinates[:, 2].min()
		self.coordinates = self.coordinates[ mask ]
		self.colors = self.colors[ mask ]
		points = np.hstack( [ self.coordinates, self.colors ] )
		with open( output_file, 'w' ) as outfile :
			outfile.write( self.ply_header.format( vertex_count=len(self.coordinates) ) )
			np.savetxt( outfile, points, '%f %f %f %d %d %d' )


#
# Stereo disparity class
#
class StereoBM( object ) :
	
	#
	# Initialize the StereoBM, and display the disparity map
	#
	def __init__( self, calibration, input_folder ) :
		
		# Store the stereo calibration parameters
		self.calibration = calibration

		# Read the images
		self.left_image = cv2.imread( '{}/left.png'.format( input_folder ), cv2.CV_LOAD_IMAGE_GRAYSCALE )
		self.right_image = cv2.imread( '{}/right.png'.format( input_folder ), cv2.CV_LOAD_IMAGE_GRAYSCALE )

		# Remap the images
		self.left_image = cv2.remap( self.left_image, calibration['left_map'][0], calibration['left_map'][1], cv2.INTER_LINEAR )
		self.right_image = cv2.remap( self.right_image, calibration['right_map'][0], calibration['right_map'][1], cv2.INTER_LINEAR )

		# StereoBM parameters
		self.preset = cv2.STEREO_BM_BASIC_PRESET
	#	self.preset = cv2.STEREO_BM_NORMALIZED_RESPONSE_PRESET
	#	self.preset = cv2.STEREO_BM_FISH_EYE_PRESET
	#	self.preset = cv2.STEREO_BM_NARROW_PRESET
		self.ndisparities = 48
		self.SADWindowSize = 9

		# Display window
		cv2.namedWindow( 'Disparity map' )
		cv2.createTrackbar( 'ndisparities', 'Disparity map', self.ndisparities, 200, self.Setndisparities )
		cv2.createTrackbar( 'SADWindowSize', 'Disparity map', self.SADWindowSize, 255, self.SetSADWindowSize )
		while True :
			self.UpdateDisparity()
			image = cv2.applyColorMap( self.bm_disparity_img, cv2.COLORMAP_JET )
			cv2.imshow( 'Disparity map', cv2.pyrDown( image ) )
			key = cv2.waitKey( 1 ) & 0xFF
			if key == 27 : break
			elif key == ord('m') :
				print( 'Exporting point cloud...' )
				point_cloud = PointCloud( cv2.reprojectImageTo3D( self.bm_disparity, self.calibration['Q'] ),
					cv2.cvtColor( self.left_image, cv2.COLOR_GRAY2RGB ) )
				point_cloud.WritePly( 'mesh-{}-{}.ply'.format( self.ndisparities, self.SADWindowSize ) )
				print( 'Done.' )
		cv2.destroyAllWindows()
	
	#
	# Set the number ot disparities (multiple of 16)
	#
	def Setndisparities( self, value ) :
		if value % 16 :	value -= value % 16
		self.ndisparities = value
		cv2.setTrackbarPos( 'ndisparities', 'Disparity map', self.ndisparities )
		self.UpdateDisparity()

	#
	# Set the search window size (odd, and in range [5...255])
	#
	def SetSADWindowSize( self, value ) :
		if value < 5 : value = 5
		elif not value % 2 : value += 1
		self.SADWindowSize = value
		cv2.setTrackbarPos( 'SADWindowSize', 'Disparity map', self.SADWindowSize )
		self.UpdateDisparity()

	#
	# Compute the stereo correspondence
	#
	def UpdateDisparity( self ):
		
		self.bm = cv2.StereoBM( self.preset, self.ndisparities, self.SADWindowSize )
		self.bm_disparity = self.bm.compute( self.left_image, self.right_image, disptype=cv2.CV_32F )
		self.bm_disparity_img = self.bm_disparity * 255.99 / ( self.bm_disparity.min() - self.bm_disparity.max() )
		self.bm_disparity_img = self.bm_disparity_img.astype( np.uint8 )


#
# Stereo disparity class
#
class StereoSGBM( object ) :
	
	#
	# Initialize the StereoSGBM, and display the disparity map
	#
	def __init__( self, calibration, input_folder ) :
		
		# Store the stereo calibration parameters
		self.calibration = calibration

		# Read the images
		self.left_image = cv2.imread( '{}/left.png'.format( input_folder ), cv2.CV_LOAD_IMAGE_GRAYSCALE )
		self.right_image = cv2.imread( '{}/right.png'.format( input_folder ), cv2.CV_LOAD_IMAGE_GRAYSCALE )

		# Remap the images
		self.left_image = cv2.remap( self.left_image, calibration['left_map'][0], calibration['left_map'][1], cv2.INTER_LINEAR )
		self.right_image = cv2.remap( self.right_image, calibration['right_map'][0], calibration['right_map'][1], cv2.INTER_LINEAR )

		# StereoSGBM parameters
		self.min_disparity = 16
		self.num_disp = 96
		self.sad_window_size = 3
		self.uniqueness = 10
		self.speckle_window_size = 100
		self.speckle_range = 32
		self.P1 = 216
		self.P2 = 864
		self.max_disparity = 1
		self.full_dp = False

		# Display window
		cv2.namedWindow( 'Disparity map' )
		cv2.createTrackbar( 'min_disparity', 'Disparity map', self.min_disparity, 200, self.SetMinDisparity )
		cv2.createTrackbar( 'num_disp', 'Disparity map', self.num_disp, 200, self.SetNumDisp )
		cv2.createTrackbar( 'sad_window_size', 'Disparity map', self.sad_window_size, 200, self.SetSadWindowSize )
		cv2.createTrackbar( 'uniqueness', 'Disparity map', self.uniqueness, 200, self.SetUniqueness )
		cv2.createTrackbar( 'speckle_window_size', 'Disparity map', self.speckle_window_size, 200, self.SetSpeckleWindowSize )
		cv2.createTrackbar( 'speckle_range', 'Disparity map', self.speckle_range, 200, self.SetSpeckleRange )
		cv2.createTrackbar( 'P1', 'Disparity map', self.P1, 200, self.SetP1 )
		cv2.createTrackbar( 'P2', 'Disparity map', self.P2, 200, self.SetP2 )
		cv2.createTrackbar( 'max_disparity', 'Disparity map', self.max_disparity, 200, self.SetMaxDisparity )
		
		while True :
			
			self.UpdateDisparity()
			image = cv2.applyColorMap( self.bm_disparity_img, cv2.COLORMAP_JET )
			cv2.imshow( 'Disparity map', cv2.pyrDown( image ) )
			key = cv2.waitKey( 1 ) & 0xFF
			if key == 27 : break
			elif key == ord('m') :
				print( 'Exporting point cloud...' )
				point_cloud = PointCloud( cv2.reprojectImageTo3D( self.bm_disparity, self.calibration['Q'] ),
					cv2.cvtColor( self.left_image, cv2.COLOR_GRAY2RGB ) )
				point_cloud.WritePly( 'mesh-{}-{}.ply'.format( self.ndisparities, self.SADWindowSize ) )
				print( 'Done.' )
				
		cv2.destroyAllWindows()
	
	#
	# Set the number ot disparities (multiple of 16)
	#
	def SetMinDisparity( self, value ) :
		if value % 16 :	value -= value % 16
		self.min_disparity = value
		cv2.setTrackbarPos( 'min_disparity', 'Disparity map', self.min_disparity )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetNumDisp( self, value ) :
		self.num_disp = value
		cv2.setTrackbarPos( 'num_disp', 'Disparity map', self.num_disp )
		self.UpdateDisparity()

	#
	# Set the search window size (odd, and in range [5...255])
	#
	def SetSadWindowSize( self, value ) :
		if value < 5 : value = 5
		elif not value % 2 : value += 1
		self.SADWindowSize = value
		cv2.setTrackbarPos( 'SADWindowSize', 'Disparity map', self.SADWindowSize )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetUniqueness( self, value ) :
		self.uniqueness = value
		cv2.setTrackbarPos( 'uniqueness', 'Disparity map', self.uniqueness )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetSpeckleWindowSize( self, value ) :
		self.speckle_window_size = value
		cv2.setTrackbarPos( 'speckle_window_size', 'Disparity map', self.speckle_window_size )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetSpeckleRange( self, value ) :
		self.speckle_range = value
		cv2.setTrackbarPos( 'speckle_range', 'Disparity map', self.speckle_range )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetP1( self, value ) :
		self.P1 = value
		cv2.setTrackbarPos( 'P1', 'Disparity map', self.P1 )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetP2( self, value ) :
		self.P2 = value
		cv2.setTrackbarPos( 'P2', 'Disparity map', self.P2 )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetMaxDisparity( self, value ) :
		self.max_disparity = value
		cv2.setTrackbarPos( 'max_disparity', 'Disparity map', self.max_disparity )
		self.UpdateDisparity()

	#
	# Compute the stereo correspondence
	#
	def UpdateDisparity( self ):
		
		self.bm = cv2.StereoSGBM( minDisparity=self.min_disparity,
			numDisparities=self.num_disp,
			SADWindowSize=self.sad_window_size,
			uniquenessRatio=self.uniqueness,
			speckleWindowSize=self.speckle_window_size,
			speckleRange=self.speckle_range,
			disp12MaxDiff=self.max_disparity,
			P1=self.P1,
			P2=self.P2,
			fullDP=self.full_dp )

		self.bm_disparity = self.bm.compute( self.left_image, self.right_image )
		
		self.bm_disparity_img = self.bm_disparity.astype( np.float32 ) / 16.0
