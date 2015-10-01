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
import time
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
		self.button_cross = QtGui.QPushButton( 'Cross', self )
		self.button_cross.clicked.connect( self.Cross )
		self.button_chessboard = QtGui.QPushButton( 'Chessboard', self )
		self.button_chessboard.clicked.connect( self.Chessboard )
		self.button_calibration = QtGui.QPushButton( 'Calibration', self )
		self.button_calibration.clicked.connect( self.Calibration )
		self.button_disparity = QtGui.QPushButton( 'Disparity', self )
		self.button_disparity.clicked.connect( self.Disparity )
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
		self.layout_controls.addWidget( self.button_cross )
		self.layout_controls.addWidget( self.button_chessboard )
		self.layout_controls.addWidget( self.button_calibration )
		self.layout_controls.addWidget( self.button_disparity )
		self.layout_controls.addWidget( self.button_reconstruction )
		self.layout_controls.addLayout( self.layout_pattern_size )
		self.layout_global = QtGui.QVBoxLayout( self )
		self.layout_global.addWidget( self.camera )
		self.layout_global.addLayout( self.layout_controls )

	#
	# Chessboard finder
	#
	def Cross( self ) :

		self.camera.cross_enabled = not self.camera.cross_enabled

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
	# Disparity map
	#
	def Disparity( self ) :

		self.camera.disparity_enabled = not self.camera.disparity_enabled

	#
	# 3D reconstruction
	#
	def Reconstruction( self ) :

		Disparity.WritePly( 'mesh-{}.ply'.format( time.strftime( '%Y%m%d_%H%M%S' ) ),
			cv2.reprojectImageTo3D( self.camera.disparity, self.calibration['Q'] ),
			cv2.cvtColor( self.camera.image_left, cv2.COLOR_BGR2RGB ) )

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

