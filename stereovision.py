#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to calibrate stereo cameras, and to recontruct a 3D scene
#



#
# External dependencies
#
import glob
import pickle
import sys
import PySide.QtCore as qtcore
import PySide.QtGui as qtgui
import Calibration
import Camera
import QtDisparity


#
# Main application of stereovision
#
class StereoVision( qtgui.QWidget ) :


	#
	# Initialisation
	#
	def __init__( self, parent = None ) :
		
		# Initialise QWidget
		super( StereoVision, self ).__init__( parent )
		
		# Create the widget for the stereo reconstruction
		self.stereosgbm = QtDisparity.StereoSGBM()
		
		# Set the window title
		self.setWindowTitle( 'StereoVision' )

		# Set the window size
		self.setGeometry( qtcore.QRect(10, 10, 521, 151) )

		# Buttons
		self.button_acquisition = qtgui.QPushButton( 'Acquisition', self )
		self.button_acquisition.clicked.connect( self.Acquisition )
		self.button_calibration = qtgui.QPushButton( 'Calibration', self )
		self.button_calibration.clicked.connect( self.Calibration )
		self.button_reconstruction = qtgui.QPushButton( 'Reconstruction', self )
		self.button_reconstruction.clicked.connect( self.Reconstruction )
		
		# Calibration pattern size
		self.pattern_size = ( 15, 10 )
		self.label_pattern_size = qtgui.QLabel( self )
		self.label_pattern_size.setText( 'Calibration pattern size :' )
		self.spinbox_pattern_rows = qtgui.QSpinBox( self )
		self.spinbox_pattern_rows.setValue( 15 )
		self.spinbox_pattern_rows.valueChanged.connect( self.UpdatePatternSize )
		self.spinbox_pattern_cols = qtgui.QSpinBox( self )
		self.spinbox_pattern_cols.setValue( 10 )
		self.spinbox_pattern_cols.valueChanged.connect( self.UpdatePatternSize )

		# Widget layout
		self.layout_pattern_size = qtgui.QHBoxLayout()
		self.layout_pattern_size.addWidget( self.label_pattern_size )
		self.layout_pattern_size.addWidget( self.spinbox_pattern_rows )
		self.layout_pattern_size.addWidget( self.spinbox_pattern_cols )
		self.layout_global = qtgui.QVBoxLayout( self )
		self.layout_global.addWidget( self.button_acquisition )
		self.layout_global.addWidget( self.button_calibration )
		self.layout_global.addWidget( self.button_reconstruction )
		self.layout_global.addLayout( self.layout_pattern_size )
		
	#
	# Live display of the camera images
	#
	def Acquisition( self ) :
		
		# Launch the stereo camera viewer
		Camera.VmbStereoViewer( self.pattern_size )

	#
	# Stereo camera calibration
	#
	def Calibration( self ) :

		# Select the folder containing the calibration files
		selected_directory = qtgui.QFileDialog.getExistingDirectory()
		if not selected_directory : return
		
		# Calibrate the left camera
		print( '\n~~~ Left camera calibration ~~~\n' )
		camera_calibration_left = Calibration.CameraCalibration( sorted( glob.glob( '{}/left*.png'.format( selected_directory ) ) ),
			self.pattern_size )
		
		# Write the results
		with open( 'camera-calibration-left.pkl', 'wb') as output_file :
			pickle.dump( camera_calibration_left, output_file, pickle.HIGHEST_PROTOCOL )
			
		# Calibrate the right camera
		print( '\n~~~ Right camera calibration ~~~\n' )
		camera_calibration_right = Calibration.CameraCalibration( sorted( glob.glob( '{}/right*.png'.format( selected_directory ) ) ),
			self.pattern_size )

		# Write the results
		with open( 'camera-calibration-right.pkl', 'wb') as output_file :
			pickle.dump( camera_calibration_right, output_file, pickle.HIGHEST_PROTOCOL )

		# Calibrate the stereo cameras
		print( '\n~~~ Stereo camera calibration ~~~\n' )
		stereo_calibration = Calibration.StereoCameraCalibration( camera_calibration_left, camera_calibration_right )
		
		# Write results
		with open( 'stereo-calibration.pkl' , 'wb') as output_file :
			pickle.dump( stereo_calibration, output_file, pickle.HIGHEST_PROTOCOL )

	#
	# 3D reconstruction
	#
	def Reconstruction( self ) :

		# Show the widget used to reconstruct the 3D mesh
		self.stereosgbm.show()

	#
	# Update the calibration pattern size
	#
	def UpdatePatternSize( self, _ ) :
		
		# Get the calibration pattern dimensions
		self.pattern_size = ( self.spinbox_pattern_rows.value(), self.spinbox_pattern_cols.value() )


#
# Main application
#
application = qtgui.QApplication( sys.argv )
widget = StereoVision()
widget.show()
sys.exit( application.exec_() )


