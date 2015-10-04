# -*- coding:utf-8 -*- 


#
# Qt interface for the disparity module
#


#
# External dependencies
#
import pickle
import sys
import cv2
import numpy as np
from PySide import QtCore
from PySide import QtGui


#
# Export the point cloud to a PLY file
#
def WritePly( filename, coordinates, colors ) :
	
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
''' )
	coordinates = coordinates.reshape(-1, 3)
	colors = colors.reshape(-1, 3)
	mask = coordinates[:, 2] > coordinates[:, 2].min()
	coordinates = coordinates[ mask ]
	colors = colors[ mask ]
	points = np.hstack( [ coordinates, colors ] )
	with open( filename, 'w' ) as output_file :
		output_file.write( ply_header.format( vertex_count=len(coordinates) ) )
		np.savetxt( output_file, points, '%f %f %f %d %d %d' )


#
# Customize the Qt widget to setup the stereo BM
#
class StereoSGBM( QtGui.QWidget ) :

	#
	# Initialisation
	#
	def __init__( self, parent = None ) :
		
		#
		# Initialize the StereoBM
		#
		
		# StereoSGBM parameters
		self.min_disparity = 16
		self.max_disparity = 96
		self.sad_window_size = 3
		self.uniqueness_ratio = 10
		self.speckle_window_size = 100
		self.speckle_range = 32
		self.p1 = 8 * 3 * self.sad_window_size ** 2
		self.p2 = 32 * 3 * self.sad_window_size ** 2
		self.max_difference = 1
		self.full_dp = False

		#
		# Initialize the interface
		#

		# Initialise QWidget
		super( StereoSGBM, self ).__init__( parent )

		# Set the window title
		self.setWindowTitle( 'StereoSGBM' )

		# Set the window size
		self.setGeometry( QtCore.QRect(10, 10, 621, 251) )

		# StereoSGBM parameter controls
		self.spinbox_min_disparity = QtGui.QSpinBox( self )
		self.spinbox_min_disparity.setMaximum( 240 )
		self.spinbox_min_disparity.setSingleStep( 16 )
		self.spinbox_min_disparity.setValue( self.min_disparity )
		self.spinbox_max_disparity = QtGui.QSpinBox( self )
		self.spinbox_max_disparity.setMaximum( 240 )
		self.spinbox_max_disparity.setSingleStep( 16 )
		self.spinbox_max_disparity.setValue( self.max_disparity )
		self.spinbox_sad_window_size = QtGui.QSpinBox( self )
		self.spinbox_sad_window_size.setMinimum( 3 )
		self.spinbox_sad_window_size.setMaximum( 11 )
		self.spinbox_sad_window_size.setSingleStep( 2 )
		self.spinbox_sad_window_size.setValue( self.sad_window_size )
		self.spinbox_uniqueness_ratio = QtGui.QSpinBox( self )
		self.spinbox_uniqueness_ratio.setValue( self.uniqueness_ratio )
		self.spinbox_speckle_window_size = QtGui.QSpinBox( self )
		self.spinbox_speckle_window_size.setMaximum( 240 )
		self.spinbox_speckle_window_size.setValue( self.speckle_window_size )
		self.spinbox_speckle_range = QtGui.QSpinBox( self )
		self.spinbox_speckle_range.setValue( self.speckle_range )
		self.spinbox_p1 = QtGui.QSpinBox( self )
		self.spinbox_p1.setMaximum( 2000 )
		self.spinbox_p1.setValue( self.p1 )
		self.spinbox_p2 = QtGui.QSpinBox( self )
		self.spinbox_p2.setMaximum( 2000 )
		self.spinbox_p2.setValue( self.p2 )
		self.spinbox_max_difference = QtGui.QSpinBox( self )
		self.spinbox_max_difference.setValue( self.max_difference )

		# Buttons
		self.button_apply = QtGui.QPushButton( 'Apply', self )
		self.button_apply.clicked.connect( self.UpdateDisparity )
		self.button_save = QtGui.QPushButton( 'Save', self )
		self.button_save.setEnabled( False )
		self.button_save.clicked.connect( self.SavePointCloud )

		# Widget layout
		self.layout_controls = QtGui.QGridLayout()
		self.layout_controls.addWidget( QtGui.QLabel( 'Minimum disparity', self ), 0, 0 )
		self.layout_controls.addWidget( self.spinbox_min_disparity, 0, 1 )
		self.layout_controls.addWidget( QtGui.QLabel( 'Maximum disparity', self ), 1, 0 )
		self.layout_controls.addWidget( self.spinbox_max_disparity, 1, 1 )
		self.layout_controls.addWidget( QtGui.QLabel( 'SAD window size', self ), 2, 0 )
		self.layout_controls.addWidget( self.spinbox_sad_window_size, 2, 1 )
		self.layout_controls.addWidget( QtGui.QLabel( 'Uniqueness ratio', self ), 3, 0 )
		self.layout_controls.addWidget( self.spinbox_uniqueness_ratio, 3, 1 )
		self.layout_controls.addWidget( QtGui.QLabel( 'Spekle window size', self ), 4, 0 )
		self.layout_controls.addWidget( self.spinbox_speckle_window_size, 4, 1 )
		self.layout_controls.addWidget( QtGui.QLabel( 'Spekle range', self ), 5, 0 )
		self.layout_controls.addWidget( self.spinbox_speckle_range, 5, 1 )
		self.layout_controls.addWidget( QtGui.QLabel( 'P1', self ), 6, 0 )
		self.layout_controls.addWidget( self.spinbox_p1, 6, 1 )
		self.layout_controls.addWidget( QtGui.QLabel( 'P2', self ), 7, 0 )
		self.layout_controls.addWidget( self.spinbox_p2, 7, 1 )
		self.layout_controls.addWidget( QtGui.QLabel( 'Maximum difference', self ), 8, 0 )
		self.layout_controls.addWidget( self.spinbox_max_difference, 8, 1 )
		self.layout_buttons = QtGui.QHBoxLayout()
		self.layout_buttons.addWidget( self.button_apply )
		self.layout_buttons.addWidget( self.button_save )
		self.layout_global = QtGui.QVBoxLayout( self )
		self.layout_global.addLayout( self.layout_controls )
		self.layout_global.addLayout( self.layout_buttons )
		
	#
	# Load the images
	#
	def LoadImages( self, left_image, right_image ) :

			self.left_image = left_image
			self.right_image = right_image

	#
	# Save the resulting point cloud
	#
	def SavePointCloud( self ) :
		
		print( 'Exporting point cloud...' )
		WritePly( 'mesh-{}-{}.ply'.format( self.min_disparity, self.sad_window_size ),
			cv2.reprojectImageTo3D( self.bm_disparity, self.calibration['Q'] ),
			cv2.cvtColor( self.left_image, cv2.COLOR_BGR2RGB ) )
		print( 'Done.' )

	#
	# Compute the stereo correspondence
	#
	def UpdateDisparity( self ) :

		# Get the parameters
		self.min_disparity = self.spinbox_min_disparity.value()
		self.max_disparity = self.spinbox_max_disparity.value()
		self.sad_window_size = self.spinbox_sad_window_size.value()
		self.uniqueness_ratio = self.spinbox_uniqueness_ratio.value()
		self.speckle_window_size = self.spinbox_speckle_window_size.value()
		self.speckle_range = self.spinbox_speckle_range.value()
		self.max_difference = self.spinbox_max_difference.value()
		self.p1 = self.spinbox_p1.value()
		self.p2 = self.spinbox_p2.value()

		# Create the disparity object
		print( "Compute disparity..." )
		self.bm = cv2.StereoSGBM( minDisparity = self.min_disparity,
			numDisparities = self.max_disparity,
			SADWindowSize = self.sad_window_size,
			uniquenessRatio = self.uniqueness_ratio,
			speckleWindowSize = self.speckle_window_size,
			speckleRange = self.speckle_range,
			disp12MaxDiff = self.max_difference,
			P1 = self.p1,
			P2 = self.p2,
			fullDP = self.full_dp )
		
		# Compute the disparity map
		self.bm_disparity = self.bm.compute( self.left_image, self.right_image ).astype( np.float32 ) / 16.0
		
		# Create the disparity image for display
		self.bm_disparity_img = self.bm_disparity
		cv2.normalize( self.bm_disparity_img, self.bm_disparity_img, 0, 255, cv2.NORM_MINMAX )
#		self.bm_disparity_img = ( self.bm_disparity - self.min_disparity ) / self.max_disparity
		self.bm_disparity_img = self.bm_disparity_img.astype( np.uint8 )
#		self.bm_disparity_img = cv2.pyrDown( self.bm_disparity_img )
		self.bm_disparity_img = cv2.applyColorMap( self.bm_disparity_img, cv2.COLORMAP_JET )
#		self.bm_disparity_img = cv2.cvtColor( self.bm_disparity_img, cv2.COLOR_BGR2RGB )
		
		# Display the disparity map
		cv2.imshow( 'Disparity map', self.bm_disparity_img )
		
		# Enable the button to export the 3D mesh
		self.button_save.setEnabled( True )

