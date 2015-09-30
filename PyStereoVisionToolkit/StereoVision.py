#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to calibrate stereo cameras, and to recontruct a 3D scene
#



#
# External dependencies
#
import os
import pickle
import sys
import cv2
from PySide import QtCore
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
		super( StereoVision, self ).__init__( parent, QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint )
		
		# Load the calibration parameter file, if it exists
		self.calibration = None
		if os.path.isfile( '{}/calibration.pkl'.format(Calibration.calibration_directory) ) :
			with open( '{}/calibration.pkl'.format(Calibration.calibration_directory) , 'rb') as calibration_file :
				self.calibration = pickle.load( calibration_file )
		
		# Create the widget for the stereo reconstruction
		self.stereosgbm = Disparity.StereoSGBM()
		
		# Set the window title
		self.setWindowTitle( 'StereoVision' )
		
		# Camera viewer
		self.camera = Camera.QtCameraViewer( self, self.calibration )

		# Buttons
		self.button_chessboard = QtGui.QPushButton( 'Chessboard', self )
		self.button_chessboard.clicked.connect( self.Chessboard )
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
		self.layout_controls = QtGui.QHBoxLayout()
		self.layout_controls.addWidget( self.button_chessboard )
		self.layout_controls.addWidget( self.button_calibration )
		self.layout_controls.addWidget( self.button_reconstruction )
		self.layout_controls.addLayout( self.layout_pattern_size )
		self.layout_global = QtGui.QVBoxLayout( self )
		self.layout_global.addWidget( self.camera )
		self.layout_global.addLayout( self.layout_controls )

	#
	# Chessboard finder
	#
	def Chessboard( self ) :

		self.camera.chessboard_enabled = not self.camera.chessboard_enabled

	#
	# Stereo camera calibration
	#
	def Calibration( self ) :

		# Calibrate the stereo cameras
		self.calibration = Calibration.StereoCameraCalibration()
		self.camera.calibration = self.calibration
		msgBox = QtGui.QMessageBox()
		msgBox.setText( 'Calibration done !' )
		msgBox.exec_()

	#
	# 3D reconstruction
	#
	def Reconstruction( self ) :

		self.camera.disparity_enabled = not self.camera.disparity_enabled

		# Read images for the 3D reconstruction
#		left_image = cv2.imread( 'left.png' )
#		right_image = cv2.imread( 'right.png' )

		# Select the image for 3D reconstruction
#		selected_files, _ = QtGui.QFileDialog.getOpenFileNames()
#		if len( selected_files ) != 2 : return
#		selected_files = sorted( selected_files )
		
		# Read the images
#		left_image = cv2.imread( selected_files[0] )
#		right_image = cv2.imread( selected_files[1] )

		# Undistort the images according to the stereo camera calibration parameters
#		left_image, right_image = Calibration.StereoRectification( self.calibration, left_image, right_image )
		
		# Show the widget used to reconstruct the 3D mesh
#		self.stereosgbm.LoadImages( left_image, right_image )
#		self.stereosgbm.show()
#		self.stereosgbm.UpdateDisparity()

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

