# -*- coding:utf-8 -*- 


#
# Qt interface for the disparity module
#


#
# External dependencies
#
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
	mask = coordinates[:, 2] > coordinates[:, 2].min()+10
	coordinates = coordinates[ mask ]
	colors = colors[ mask ]
	mask = coordinates[:, 2] < coordinates[:, 2].max()-10
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
		
		# Initialize the StereoSGBM
		self.min_disparity = 0
		self.max_disparity = 16
		self.sad_window_size = 3
		self.uniqueness_ratio = 10
		self.speckle_window_size = 100
		self.speckle_range = 32
		self.p1 = 8 * 3 * self.sad_window_size ** 2
		self.p2 = 32 * 3 * self.sad_window_size ** 2
		self.max_difference = 1
		self.full_dp = False

		# Initialise QWidget
		super( StereoSGBM, self ).__init__( parent )

		# Set the window title
		self.setWindowTitle( 'StereoSGBM' )

		# Widget elements
		self.spinbox_min_disparity = QtGui.QSpinBox( self )
		self.spinbox_min_disparity.setMaximum( 240 )
		self.spinbox_min_disparity.setValue( self.min_disparity )
		self.spinbox_max_disparity = QtGui.QSpinBox( self )
		self.spinbox_max_disparity.setMaximum( 320 )
		self.spinbox_max_disparity.setSingleStep( 16 )
		self.spinbox_max_disparity.setValue( self.max_disparity )
		self.spinbox_sad_window_size = QtGui.QSpinBox( self )
		self.spinbox_sad_window_size.setMinimum( 1 )
		self.spinbox_sad_window_size.setMaximum( 19 )
		self.spinbox_sad_window_size.setSingleStep( 2 )
		self.spinbox_sad_window_size.setValue( self.sad_window_size )
		self.spinbox_uniqueness_ratio = QtGui.QSpinBox( self )
		self.spinbox_uniqueness_ratio.setMaximum( 100 )
		self.spinbox_uniqueness_ratio.setValue( self.uniqueness_ratio )
		self.spinbox_speckle_window_size = QtGui.QSpinBox( self )
		self.spinbox_speckle_window_size.setMaximum( 320 )
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
		self.checkbox_full_dp = QtGui.QCheckBox( self )
		if self.full_dp : self.checkbox_full_dp.setCheckState( True )
		self.button_apply = QtGui.QPushButton( 'Apply', self )
		self.button_apply.clicked.connect( self.UpdateDisparity )

		# Widget layout
		self.layout_controls = QtGui.QFormLayout()
		self.layout_controls.addRow( 'Minimum disparity', self.spinbox_min_disparity )
		self.layout_controls.addRow( 'Maximum disparity', self.spinbox_max_disparity )
		self.layout_controls.addRow( 'SAD window size', self.spinbox_sad_window_size )
		self.layout_controls.addRow( 'Uniqueness ratio', self.spinbox_uniqueness_ratio )
		self.layout_controls.addRow( 'Spekle window size', self.spinbox_speckle_window_size )
		self.layout_controls.addRow( 'Spekle range', self.spinbox_speckle_range )
		self.layout_controls.addRow( 'P1', self.spinbox_p1 )
		self.layout_controls.addRow( 'P2', self.spinbox_p2 )
		self.layout_controls.addRow( 'Maximum difference', self.spinbox_max_difference )
		self.layout_controls.addRow( 'Full scale DP', self.checkbox_full_dp )
		self.layout_global = QtGui.QVBoxLayout( self )
		self.layout_global.addLayout( self.layout_controls )
		self.layout_global.addWidget( self.button_apply )
		self.layout_global.setSizeConstraint( QtGui.QLayout.SetFixedSize )

		# Set the Escape key to close the application
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Escape ), self ).activated.connect( self.close )

		# Initialize the disparity object
		self.UpdateDisparity()

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
		self.full_dp = self.checkbox_full_dp.checkState()

		# Create the disparity object
		self.sgbm = cv2.StereoSGBM( minDisparity = self.min_disparity,
			numDisparities = self.max_disparity,
			SADWindowSize = self.sad_window_size,
			uniquenessRatio = self.uniqueness_ratio,
			speckleWindowSize = self.speckle_window_size,
			speckleRange = self.speckle_range,
			disp12MaxDiff = self.max_difference,
			P1 = self.p1,
			P2 = self.p2,
			fullDP = self.full_dp )
		
	#
	# Compute the stereo correspondence
	#
	def ComputeDisparity( self, left_image, right_image ) :

		# Compute the disparity map
		self.disparity = self.sgbm.compute( left_image, right_image ).astype( np.float32 ) / 16.0

	#	self.disparity[0:50,:] = 0
	#	self.disparity[210:240,:] = 0
	#	self.disparity[:,0:70] = 0
	#	self.disparity[:,250:320] = 0
		
		# Create the disparity image for display
		self.disparity_image = self.disparity
		cv2.normalize( self.disparity_image, self.disparity_image, 0, 255, cv2.NORM_MINMAX )
#		self.disparity_image = ( self.disparity - self.disparity.min() ) / ( self.disparity.max() - self.disparity.min() )
		self.disparity_image = self.disparity_image.astype( np.uint8 )
		self.disparity_image = cv2.cvtColor( self.disparity_image, cv2.COLOR_GRAY2RGB )
#		self.disparity_image = cv2.applyColorMap( self.disparity_image, cv2.COLORMAP_JET )
#		self.disparity_image = cv2.cvtColor( self.disparity_image, cv2.COLOR_BGR2RGB )
