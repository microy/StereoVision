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
		
		# Calibration pattern size
		self.pattern_size = ( 15, 10 )

		# Set the window title
		self.setWindowTitle( 'Stereovision' )

		# Set the window size
		self.setGeometry( qtcore.QRect(10, 10, 521, 151) )

		# Buttons
		self.button_live = qtgui.QPushButton( 'Live', self )
		self.button_live.clicked.connect( self.Live )
		self.button_calibration = qtgui.QPushButton( 'Calibration', self )
		self.button_calibration.clicked.connect( self.Calibration )
		self.button_reconstruction = qtgui.QPushButton( 'Reconstruction', self )
		self.button_reconstruction.clicked.connect( self.Reconstruction )

		# Widget layout
		self.layout_global = qtgui.QVBoxLayout( self )
		self.layout_global.addWidget( self.button_live )
		self.layout_global.addWidget( self.button_calibration )
		self.layout_global.addWidget( self.button_reconstruction )
		
		
	#
	# Live display of the camera images
	#
	def Live( self ) :
		
		Camera.VmbStereoViewer( self.pattern_size )


	#
	# Stereo camera calibration
	#
	def Calibration( self ) :

		# Select the folder containing the calibration files
		selected_directory = qtgui.QFileDialog.getExistingDirectory()

		# Calibrate the left camera
		print( '\n~~~ Left camera calibration ~~~\n' )
		cam1 = Calibration.CameraCalibration( sorted( glob.glob( '{}/left*.png'.format( selected_directory ) ) ),
			self.pattern_size )
		
		# Write the results
		with open( 'camera-calibration-left.pkl', 'wb') as output_file :
			pickle.dump( cam1, output_file, pickle.HIGHEST_PROTOCOL )
			
		# Calibrate the right camera
		print( '\n~~~ Right camera calibration ~~~\n' )
		cam2 = Calibration.CameraCalibration( sorted( glob.glob( '{}/right*.png'.format( selected_directory ) ) ),
			self.pattern_size )

		# Write the results
		with open( 'camera-calibration-right.pkl', 'wb') as output_file :
			pickle.dump( cam2, output_file, pickle.HIGHEST_PROTOCOL )

		# Calibrate the stereo cameras
		print( '\n~~~ Stereo camera calibration ~~~\n' )
		calibration = Calibration.StereoCameraCalibration( cam1, cam2 )
		
		# Write results
		with open( 'stereo-calibration.pkl' , 'wb') as output_file :
			pickle.dump( calibration, output_file, pickle.HIGHEST_PROTOCOL )

	#
	# 3D reconstruction
	#
	def Reconstruction( self ) :

		pass


#
# Main application
#
application = qtgui.QApplication( sys.argv )
widget = StereoVision()
widget.show()
sys.exit( application.exec_() )


