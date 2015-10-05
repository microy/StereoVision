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
import numpy as np
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyStereoVisionToolkit import Calibration
from PyStereoVisionToolkit import Camera
from PyStereoVisionToolkit import Disparity
from PyStereoVisionToolkit import PointCloudViewer


#
# Main stereovision application
#
class StereoVision( QtGui.QApplication ) :

	#
	# Initialization
	#
	def __init__( self ) :

		# Initialize parent class
		super( StereoVision, self ).__init__( sys.argv )
		
		# Show the stereovision widget
		widget = StereoVisionWidget()
		widget.show()
		
		# Enter Qt main loop
		sys.exit( self.exec_() )


#
# Stereovision user interface
#
class StereoVisionWidget( QtGui.QWidget ) :

	#
	# Initialization
	#
	def __init__( self, parent = None ) :
		
		# Initialise QWidget
		super( StereoVisionWidget, self ).__init__( parent )
		
		# Load the calibration parameter file, if it exists
		self.calibration = None
		if os.path.isfile( '{}/calibration.pkl'.format(Calibration.calibration_directory) ) :
			with open( '{}/calibration.pkl'.format(Calibration.calibration_directory) , 'rb') as calibration_file :
				self.calibration = pickle.load( calibration_file )
		
		# Set the window title
		self.setWindowTitle( 'StereoVision' )
		
		# Point cloud viewer
		self.pointcloud_viewer = PointCloudViewer.PointCloudViewer()
		
		# Stereo camera widget
		self.camera_widget = Camera.StereoCameraWidget( self, self.calibration )

		# Widget elements
		self.button_cross = QtGui.QPushButton( 'Cross', self )
		self.button_cross.setCheckable( True )
		self.button_cross.setShortcut( 'F1' )
		self.button_cross.clicked.connect( self.Cross )
		self.button_chessboard = QtGui.QPushButton( 'Chessboard', self )
		self.button_chessboard.setCheckable( True )
		self.button_chessboard.setShortcut( 'F2' )
		self.button_chessboard.clicked.connect( self.Chessboard )
		self.button_calibration = QtGui.QPushButton( 'Calibration', self )
		self.button_calibration.setShortcut( 'F3' )
		if self.calibration : self.button_calibration.setIcon( self.style().standardIcon( QtGui.QStyle.SP_DialogYesButton ) )
		else : self.button_calibration.setIcon( self.style().standardIcon( QtGui.QStyle.SP_DialogNoButton ) )
		self.button_calibration.clicked.connect( self.Calibration )
		self.button_rectification = QtGui.QPushButton( 'Rectification', self )
		self.button_rectification.setCheckable( True )
		self.button_rectification.setShortcut( 'F4' )
		self.button_rectification.clicked.connect( self.Rectification )
		self.button_disparity = QtGui.QPushButton( 'Disparity', self )
		self.button_disparity.setCheckable( True )
		self.button_disparity.setShortcut( 'F5' )
		self.button_disparity.clicked.connect( self.Disparity )
		self.button_reconstruction = QtGui.QPushButton( 'Reconstruction', self )
		self.button_reconstruction.setShortcut( 'F6' )
		self.button_reconstruction.clicked.connect( self.Reconstruction )
		self.spinbox_pattern_rows = QtGui.QSpinBox( self )
		self.spinbox_pattern_rows.setValue( Calibration.pattern_size[0] )
		self.spinbox_pattern_rows.valueChanged.connect( self.UpdatePatternSize )
		self.spinbox_pattern_cols = QtGui.QSpinBox( self )
		self.spinbox_pattern_cols.setValue( Calibration.pattern_size[1] )
		self.spinbox_pattern_cols.valueChanged.connect( self.UpdatePatternSize )
		self.button_save = QtGui.QPushButton( 'Save', self )
		self.button_save.setShortcut( 'Space' )
		self.button_save.clicked.connect( self.Save )

		# Widget layout
		self.layout_pattern_size = QtGui.QHBoxLayout()
		self.layout_pattern_size.addWidget( QtGui.QLabel( 'Calibration pattern size :' ) )
		self.layout_pattern_size.addWidget( self.spinbox_pattern_rows )
		self.layout_pattern_size.addWidget( self.spinbox_pattern_cols )
		self.layout_controls = QtGui.QHBoxLayout()
		self.layout_controls.addWidget( self.button_cross )
		self.layout_controls.addWidget( self.button_chessboard )
		self.layout_controls.addWidget( self.button_calibration )
		self.layout_controls.addWidget( self.button_rectification )
		self.layout_controls.addWidget( self.button_disparity )
		self.layout_controls.addWidget( self.button_reconstruction )
		self.layout_controls.addLayout( self.layout_pattern_size )
		self.layout_controls.addWidget( self.button_save )
		self.layout_global = QtGui.QVBoxLayout( self )
		self.layout_global.addWidget( self.camera_widget )
		self.layout_global.addLayout( self.layout_controls )
		self.layout_global.setSizeConstraint( QtGui.QLayout.SetFixedSize )
		
		# Set the Escape key to close the application
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Escape ), self ).activated.connect( self.close )

	#
	# Activate the cross on the images
	#
	def Cross( self ) :

		self.camera_widget.cross_enabled = not self.camera_widget.cross_enabled

	#
	# Chessboard finder
	#
	def Chessboard( self ) :

		self.camera_widget.chessboard_enabled = not self.camera_widget.chessboard_enabled

	#
	# Stereo camera calibration
	#
	def Calibration( self ) :

		# Calibrate the stereo cameras
		self.calibration = Calibration.StereoCameraCalibration()
		self.camera_widget.calibration = self.calibration
		self.button_calibration.setIcon( self.style().standardIcon( QtGui.QStyle.SP_DialogYesButton ) )

	#
	# Image rectification
	#
	def Rectification( self ) :

		self.camera_widget.rectification_enabled = not self.camera_widget.rectification_enabled
		if self.camera_widget.rectification_enabled and self.button_disparity.isChecked() :
			self.button_disparity.click()

	#
	# Disparity map
	#
	def Disparity( self ) :

		self.camera_widget.disparity_enabled = not self.camera_widget.disparity_enabled
		if self.camera_widget.disparity_enabled and self.button_rectification.isChecked() :
			self.button_rectification.click()
		if self.camera_widget.disparity_enabled : self.camera_widget.disparity.show()
		else : self.camera_widget.disparity.hide()

	#
	# 3D reconstruction
	#
	def Reconstruction( self ) :

		self.pointcloud_viewer.show()
	#	coordinates = cv2.reprojectImageTo3D( self.camera_widget.disparity.disparity, self.calibration['Q'] )
		X, Y = np.meshgrid( np.arange( 320 ), np.arange( 240 ) )
		coordinates = np.array( (X.flatten(), Y.flatten(),
			self.camera_widget.disparity.disparity.flatten() * 0.5) ).T
		colors = cv2.cvtColor( self.camera_widget.image_left, cv2.COLOR_BGR2RGB )
		self.pointcloud_viewer.LoadPointCloud( coordinates, colors )
	#	Disparity.WritePly( 'mesh-{}.ply'.format( time.strftime( '%Y%m%d_%H%M%S' ) ), coordinates, colors )

	#
	# Update the calibration pattern size
	#
	def UpdatePatternSize( self, _ ) :
		
		# Get the calibration pattern dimensions
		Calibration.pattern_size = ( self.spinbox_pattern_rows.value(), self.spinbox_pattern_cols.value() )

	#
	# Save the stereo images
	#
	def Save( self ) :
		
		# Save images to disk 
		current_time = time.strftime( '%Y%m%d_%H%M%S' )
		print( 'Save images {} to disk...'.format(current_time) )
		if self.camera_widget.chessboard_enabled :
			cv2.imwrite( '{}/left-{}.png'.format(Calibration.calibration_directory, current_time), self.camera_widget.image_left )
			cv2.imwrite( '{}/right-{}.png'.format(Calibration.calibration_directory, current_time), self.camera_widget.image_right )
		else :
			cv2.imwrite( 'left-{}.png'.format(current_time), self.camera_widget.image_left )
			cv2.imwrite( 'right-{}.png'.format(current_time), self.camera_widget.image_right )

	#
	# Close the camera widget
	#
	def closeEvent( self, event ) :
		
		# Stop image acquisition, and close the widgets
		self.camera_widget.close()
		event.accept()
