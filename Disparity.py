# -*- coding:utf-8 -*- 


#
# Image disparity module
#


#
# External dependencies
#
import sys
import cv2
import numpy as np
import PySide.QtCore as qtcore
import PySide.QtGui as qtgui




#
# Main application to display a mesh
#
class QtDisparity( qtgui.QApplication ) :

	#
	# Initialisation
	#
	def __init__( self ) :

		# Initialize parent class
		super( QtDisparity, self ).__init__( sys.argv )
		
		# Show the widget used to display the mesh
		self.qtstereobmwidget = QtStereoBM()
		self.qtstereobmwidget.show()
		
		# Enter Qt main loop
		self.exec_()



#
# Customize the Qt widget to setup the stereo BM
#
class QtStereoBM( qtgui.QWidget ) :

	#
	# Initialisation
	#
	def __init__( self, parent = None ) :
		
		# Initialise QWidget
		super( QtStereoBM, self ).__init__( parent )

		# Set the window title
		self.setWindowTitle( 'StereoBM disparity' )

		# Widget
		self.setGeometry( qtcore.QRect(10, 10, 521, 151) )

		# Disparity layout
		self.slider_disparities = qtgui.QSlider( self )
		self.slider_disparities.setOrientation( qtcore.Qt.Horizontal )
		self.label_disparities = qtgui.QLabel( self )
		self.label_disparities.setText( 'Number of disparities' )

		# SAD window size layout
		self.slider_sad_window = qtgui.QSlider( self )
		self.slider_sad_window.setOrientation( qtcore.Qt.Horizontal )
		self.label_sad_window = qtgui.QLabel( self )
		self.label_sad_window.setText( 'SAD Window size' )

		# Apply button
		self.button_apply = qtgui.QDialogButtonBox( self )
		self.button_apply.setStandardButtons( qtgui.QDialogButtonBox.Apply )
		self.button_apply.setCenterButtons( True )

		# Widget layout
		self.layout_disparities = qtgui.QHBoxLayout()
		self.layout_disparities.addWidget( self.slider_disparities )
		self.layout_disparities.addWidget( self.label_disparities )
		self.layout_sad_window = qtgui.QHBoxLayout()
		self.layout_sad_window.addWidget( self.slider_sad_window )
		self.layout_sad_window.addWidget( self.label_sad_window )
		self.layout_vertical = qtgui.QVBoxLayout( self )
		self.layout_vertical.addLayout( self.layout_disparities )
		self.layout_vertical.addLayout( self.layout_sad_window )
		self.layout_vertical.addWidget( self.button_apply )






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
		self.speckle_range = 2
		self.P1 = 216
		self.P2 = 864
		self.max_disparity = 1
		self.full_dp = False

		# Display window
		cv2.namedWindow( 'SGBM' )
		cv2.createTrackbar( 'min_disparity', 'SGBM', self.min_disparity, 200, self.SetMinDisparity )
		cv2.createTrackbar( 'num_disp', 'SGBM', self.num_disp, 200, self.SetNumDisp )
		cv2.createTrackbar( 'sad_window_size', 'SGBM', self.sad_window_size, 11, self.SetSadWindowSize )
		cv2.createTrackbar( 'uniqueness', 'SGBM', self.uniqueness, 100, self.SetUniqueness )
		cv2.createTrackbar( 'speckle_window_size', 'SGBM', self.speckle_window_size, 200, self.SetSpeckleWindowSize )
		cv2.createTrackbar( 'speckle_range', 'SGBM', self.speckle_range, 50, self.SetSpeckleRange )
		cv2.createTrackbar( 'P1', 'SGBM', self.P1, 200, self.SetP1 )
		cv2.createTrackbar( 'P2', 'SGBM', self.P2, 200, self.SetP2 )
		cv2.createTrackbar( 'max_disparity', 'SGBM', self.max_disparity, 200, self.SetMaxDisparity )
		
		self.UpdateDisparity()

		while True :
			
			key = cv2.waitKey( 100 ) & 0xFF
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
		cv2.setTrackbarPos( 'min_disparity', 'SGBM', self.min_disparity )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetNumDisp( self, value ) :
		if value % 16 :	value -= value % 16
		self.num_disp = value
		cv2.setTrackbarPos( 'num_disp', 'SGBM', self.num_disp )
		self.UpdateDisparity()

	#
	# Set the search window size (odd, and in range [1...11])
	#
	def SetSadWindowSize( self, value ) :
		if value < 1 : value = 1
		elif not value % 2 : value += 1
		self.SADWindowSize = value
		cv2.setTrackbarPos( 'SADWindowSize', 'SGBM', self.SADWindowSize )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetUniqueness( self, value ) :
		self.uniqueness = value
		cv2.setTrackbarPos( 'uniqueness', 'SGBM', self.uniqueness )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetSpeckleWindowSize( self, value ) :
		self.speckle_window_size = value
		cv2.setTrackbarPos( 'speckle_window_size', 'SGBM', self.speckle_window_size )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetSpeckleRange( self, value ) :
		self.speckle_range = value
		cv2.setTrackbarPos( 'speckle_range', 'SGBM', self.speckle_range )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetP1( self, value ) :
		self.P1 = value
		cv2.setTrackbarPos( 'P1', 'SGBM', self.P1 )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetP2( self, value ) :
		self.P2 = value
		cv2.setTrackbarPos( 'P2', 'SGBM', self.P2 )
		self.UpdateDisparity()

	#
	# Set 
	#
	def SetMaxDisparity( self, value ) :
		self.max_disparity = value
		cv2.setTrackbarPos( 'max_disparity', 'SGBM', self.max_disparity )
		self.UpdateDisparity()

	#
	# Compute the stereo correspondence
	#
	def UpdateDisparity( self ):
		
		print( "Create SGBM..." )
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

		print( "Compute SGBM..." )
		self.bm_disparity = self.bm.compute( self.left_image, self.right_image )
		
		print( "Create disparity image..." )
		self.bm_disparity_img = self.bm_disparity.astype( np.float32 ) / 16.0
#		self.bm_disparity_img = ( self.bm_disparity_img - self.min_disparity ) / self.num_disp
		cv2.normalize( self.bm_disparity_img, self.bm_disparity_img, 0, 255, cv2.NORM_MINMAX )
		self.bm_disparity_img = self.bm_disparity_img.astype( np.uint8 )
		print self.bm_disparity_img.min(), self.bm_disparity_img.max()
		print( "Update disparity image.." )
		image = cv2.applyColorMap( self.bm_disparity_img, cv2.COLORMAP_JET )
		cv2.imshow( 'Disparity map', cv2.pyrDown( image ) )

