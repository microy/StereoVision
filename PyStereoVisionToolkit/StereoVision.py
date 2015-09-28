#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to calibrate stereo cameras, and to recontruct a 3D scene
#



#
# External dependencies
#
import os
import sys
import cv2
from PySide import QtGui
import Calibration
import Camera
import Disparity


#
# Main application of stereovision
#
class StereoVision( QtGui.QWidget ) :

	#
	# Initialisation
	#
	def __init__( self, parent = None ) :
		
		# Initialise QWidget
		super( StereoVision, self ).__init__( parent )
		
		# Create calibration directory, if necessary
		try : os.makedirs( 'Calibration' )
		except OSError :
			if not os.path.isdir( 'Calibration' ) : raise

		# Load the calibration parameter file, if it exists
		self.calibration = None
		if os.path.isfile( 'Calibration/calibration.pkl' ) :
			with open( 'Calibration/calibration.pkl' , 'rb') as calibration_file :
				self.calibration = pickle.load( calibration_file )
		
		# Create the widget for the stereo reconstruction
		self.stereosgbm = Disparity.StereoSGBM()
		
		# Set the window title
		self.setWindowTitle( 'StereoVision' )

		# Buttons
		self.button_acquisition = QtGui.QPushButton( 'Acquisition', self )
		self.button_acquisition.clicked.connect( self.Acquisition )
		self.button_calibration = QtGui.QPushButton( 'Calibration', self )
		self.button_calibration.clicked.connect( self.Calibration )
		self.button_reconstruction = QtGui.QPushButton( 'Reconstruction', self )
		self.button_reconstruction.clicked.connect( self.Reconstruction )
		
		# Calibration pattern size
		self.spinbox_pattern_rows = QtGui.QSpinBox( self )
		self.spinbox_pattern_rows.setValue( Calibration.pattern_size[0] )
		self.spinbox_pattern_rows.valueChanged.connect( self.UpdatePatternSize )
		self.spinbox_pattern_cols = QtGui.QSpinBox( self )
		self.spinbox_pattern_cols.setValue( Calibration.pattern_size[1] )
		self.spinbox_pattern_cols.valueChanged.connect( self.UpdatePatternSize )

		# Widget layout
		self.layout_pattern_size = QtGui.QHBoxLayout()
		self.layout_pattern_size.addWidget( QtGui.QLabel( 'Calibration pattern size :' ) )
		self.layout_pattern_size.addWidget( self.spinbox_pattern_rows )
		self.layout_pattern_size.addWidget( self.spinbox_pattern_cols )
		self.layout_global = QtGui.QVBoxLayout( self )
		self.layout_global.addWidget( self.button_acquisition )
		self.layout_global.addWidget( self.button_calibration )
		self.layout_global.addWidget( self.button_reconstruction )
		self.layout_global.addLayout( self.layout_pattern_size )
		
	#
	# Live display of the camera images
	#
	def Acquisition( self ) :
		
		# Launch the stereo camera viewer
		Camera.UsbStereoViewer( Calibration.pattern_size )

	#
	# Stereo camera calibration
	#
	def Calibration( self ) :

		# Calibrate the stereo cameras
		self.calibration = Calibration.StereoCameraCalibration()

	#
	# 3D reconstruction
	#
	def Reconstruction( self ) :

		# Read images for the 3D reconstruction
		left_image = cv2.imread( 'left.png' )
		right_image = cv2.imread( 'right.png' )

		# Undistort the images according to the stereo camera calibration parameters
		left_image, right_image = Calibration.StereoRectification( self.calibration, left_image, right_image )
		
		# Show the widget used to reconstruct the 3D mesh
		self.stereosgbm.LoadImages( left_image, right_image )
		self.stereosgbm.show()
		self.stereosgbm.UpdateDisparity()

	#
	# Update the calibration pattern size
	#
	def UpdatePatternSize( self, _ ) :
		
		# Get the calibration pattern dimensions
		Calibration.pattern_size = ( self.spinbox_pattern_rows.value(), self.spinbox_pattern_cols.value() )


#
# Main application
#
if __name__ == "__main__" :
	
	application = QtGui.QApplication( sys.argv )
	widget = StereoVision()
	widget.show()
	sys.exit( application.exec_() )


