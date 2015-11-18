#! /usr/bin/env python
# -*- coding:utf-8 -*-


#
# Show the images from two Allied Vision cameras
#

# External dependencies
import sys
import time
import cv2
import numpy as np
from PySide import QtCore
from PySide import QtGui
import VisionToolkit as vt

# Stereovision user interface
class StereoVisionWidget( QtGui.QWidget ) :
	# Initialization
	def __init__( self, parent = None ) :
		# Initialise QWidget
		super( StereoVisionWidget, self ).__init__( parent )
		# Load the calibration parameter file, if it exists
		self.calibration = vt.LoadCalibration()
		if not self.calibration : vt.CreateCalibrationDirectory()
		# Set the window title
		self.setWindowTitle( 'StereoVision' )
		# Stereo camera widget
		self.camera_widget = vt.VmbStereoCameraWidget( '50-0503326223', '50-0503323406' )
		# Widget elements
		self.button_cross = QtGui.QPushButton( 'Cross', self )
		self.button_cross.setCheckable( True )
		self.button_cross.setShortcut( 'F1' )
		self.button_cross.clicked.connect( self.camera_widget.ToggleCross )
		self.button_chessboard = QtGui.QPushButton( 'Chessboard', self )
		self.button_chessboard.setCheckable( True )
		self.button_chessboard.setShortcut( 'F2' )
		self.button_chessboard.clicked.connect( self.camera_widget.ToggleChessboard )
		self.button_calibration = QtGui.QPushButton( 'Calibration', self )
		self.button_calibration.setShortcut( 'F3' )
		if self.calibration : self.button_calibration.setIcon( self.style().standardIcon( QtGui.QStyle.SP_DialogYesButton ) )
		else : self.button_calibration.setIcon( self.style().standardIcon( QtGui.QStyle.SP_DialogNoButton ) )
		self.button_calibration.clicked.connect( self.Calibration )
		self.spinbox_pattern_rows = QtGui.QSpinBox( self )
		self.spinbox_pattern_rows.setValue( vt.pattern_size[0] )
		self.spinbox_pattern_rows.valueChanged.connect( self.UpdatePatternSize )
		self.spinbox_pattern_cols = QtGui.QSpinBox( self )
		self.spinbox_pattern_cols.setValue( vt.pattern_size[1] )
		self.spinbox_pattern_cols.valueChanged.connect( self.UpdatePatternSize )
		self.button_save_images = QtGui.QPushButton( 'Save Images', self )
		self.button_save_images.setShortcut( 'Space' )
		self.button_save_images.clicked.connect( self.SaveImages )
		# Widget layout
		self.layout_pattern_size = QtGui.QHBoxLayout()
		self.layout_pattern_size.addWidget( QtGui.QLabel( 'Calibration pattern size :' ) )
		self.layout_pattern_size.addWidget( self.spinbox_pattern_rows )
		self.layout_pattern_size.addWidget( self.spinbox_pattern_cols )
		self.layout_controls = QtGui.QHBoxLayout()
		self.layout_controls.addWidget( self.button_cross )
		self.layout_controls.addWidget( self.button_chessboard )
		self.layout_controls.addWidget( self.button_calibration )
		self.layout_controls.addLayout( self.layout_pattern_size )
		self.layout_controls.addWidget( self.button_save_images )
		self.layout_global = QtGui.QVBoxLayout( self )
		self.layout_global.addWidget( self.camera_widget )
		self.layout_global.addLayout( self.layout_controls )
		self.layout_global.setSizeConstraint( QtGui.QLayout.SetFixedSize )
		# Set up the keyboard shorcuts
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Escape ), self ).activated.connect( self.close )
	# Stereo camera calibration
	def Calibration( self ) :
		# Calibrate the stereo cameras
		self.calibration = vt.StereoCameraCalibration()
		self.camera_widget.calibration = self.calibration
		self.button_calibration.setIcon( self.style().standardIcon( QtGui.QStyle.SP_DialogYesButton ) )
	# Update the calibration pattern size
	def UpdatePatternSize( self, _ ) :
		# Get the calibration pattern dimensions
		vt.pattern_size = ( self.spinbox_pattern_rows.value(), self.spinbox_pattern_cols.value() )
	# Save the stereo images
	def SaveImages( self ) :
		# Save images to disk
		current_time = time.strftime( '%Y%m%d_%H%M%S' )
		print( 'Save images {} to disk...'.format(current_time) )
		if self.camera_widget.chessboard_enabled :
			cv2.imwrite( '{}/left-{}.png'.format(vt.calibration_directory, current_time), self.camera_widget.image_left )
			cv2.imwrite( '{}/right-{}.png'.format(vt.calibration_directory, current_time), self.camera_widget.image_right )
		else :
			cv2.imwrite( 'left-{}.png'.format(current_time), self.camera_widget.image_left )
			cv2.imwrite( 'right-{}.png'.format(current_time), self.camera_widget.image_right )
	# Close the camera widget
	def closeEvent( self, event ) :
		# Stop image acquisition, and close the widgets
		self.camera_widget.close()
		event.accept()

# Qt main application
def QtMain() :
	application = QtGui.QApplication( sys.argv )
	widget = StereoVisionWidget()
	widget.show()
	sys.exit( application.exec_() )

# OpenCV display
def CvCallback( frame_left, frame_right ) :
	# Put images side by side
	stereo_image = np.concatenate( ( frame_left.image, frame_right.image ), axis = 1 )
	# Resize image for display
	stereo_image = cv2.resize( stereo_image, None, fx=0.6, fy=0.6 )
	# Display the stereo image
	cv2.imshow( 'StereoVision', stereo_image )
	cv2.waitKey( 1 )

# OpenCV main application
def CvMain() :
	# Initialize the Vimba driver
	vt.VmbStartup()
	# Initialize the stereo cameras
	camera = vt.VmbStereoCamera( '50-0503326223', '50-0503323406' )
	# Connect the cameras
	camera.Open()
	# Start image acquisition
	camera.StartCapture( CvCallback )
	# Wait for user key press
	raw_input( 'Press enter to stop the capture...' )
	# Stop image acquisition
	camera.StopCapture()
	# Disconnect the camera
	camera.Close()
	# Shutdown Vimba
	vt.VmbShutdown()
	# Cleanup OpenCV
	cv2.destroyAllWindows()

#
# Main application
#
if __name__ == '__main__' :

#	CvMain()
	QtMain()
