# -*- coding:utf-8 -*-

#
# Qt interfaces for the StereoVision application
#

# External dependencies
import time
import cv2
import numpy as np
from PySide import QtCore
from PySide import QtGui
import StereoVision as sv

# Stereovision user interface
class StereoVision( QtGui.QWidget ) :
	# Signal sent to update the image in the widget
	update_stereo_images = QtCore.Signal( np.ndarray, np.ndarray )
	# Initialization
	def __init__( self, parent = None ) :
		# Initialise QWidget
		super( StereoVision, self ).__init__( parent )
		# Load the calibration parameter file, if it exists
		self.calibration = sv.LoadCalibration()
		if not self.calibration : sv.CreateCalibrationDirectory()
		# Initialize the viewing parameters
		self.chessboard_enabled = False
		self.cross_enabled = False
		self.rectification_enabled = False
		self.disparity_enabled = False
		# Set the window title
		self.setWindowTitle( 'StereoVision' )
		# Connect the signal to update the image
		self.update_stereo_images.connect( self.UpdateStereoImages )
		# Widget to display the images from the cameras
		self.image_widget = QtGui.QLabel( self )
		self.image_widget.setScaledContents( True )
		# Widget elements
		self.button_cross = QtGui.QPushButton( 'Cross', self )
		self.button_cross.setCheckable( True )
		self.button_cross.setShortcut( 'F1' )
		self.button_cross.clicked.connect( self.ToggleCross )
		self.button_chessboard = QtGui.QPushButton( 'Chessboard', self )
		self.button_chessboard.setCheckable( True )
		self.button_chessboard.setShortcut( 'F2' )
		self.button_chessboard.clicked.connect( self.ToggleChessboard )
		self.button_calibration = QtGui.QPushButton( 'Calibration', self )
		self.button_calibration.setShortcut( 'F3' )
		if self.calibration : self.button_calibration.setIcon( self.style().standardIcon( QtGui.QStyle.SP_DialogYesButton ) )
		else : self.button_calibration.setIcon( self.style().standardIcon( QtGui.QStyle.SP_DialogNoButton ) )
		self.button_calibration.clicked.connect( self.Calibration )
		self.button_rectification = QtGui.QPushButton( 'Rectification', self )
		self.button_rectification.setCheckable( True )
		self.button_rectification.setShortcut( 'F4' )
		self.button_rectification.clicked.connect( self.ToggleRectification )
		self.button_reconstruction = QtGui.QPushButton( 'Reconstruction', self )
		self.button_reconstruction.setCheckable( True )
		self.button_reconstruction.setShortcut( 'F5' )
		self.button_reconstruction.clicked.connect( self.ToggleReconstruction )
		self.spinbox_pattern_rows = QtGui.QSpinBox( self )
		self.spinbox_pattern_rows.setValue( sv.pattern_size[0] )
		self.spinbox_pattern_rows.valueChanged.connect( self.UpdatePatternSize )
		self.spinbox_pattern_cols = QtGui.QSpinBox( self )
		self.spinbox_pattern_cols.setValue( sv.pattern_size[1] )
		self.spinbox_pattern_cols.valueChanged.connect( self.UpdatePatternSize )
		self.button_save_images = QtGui.QPushButton( 'Save Images', self )
		self.button_save_images.setShortcut( 'Space' )
		self.button_save_images.clicked.connect( self.SaveImages )
		self.button_save_mesh = QtGui.QPushButton( 'Save Mesh', self )
		self.button_save_mesh.setShortcut( 'Enter' )
		self.button_save_mesh.clicked.connect( self.SaveMesh )
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
		self.layout_controls.addWidget( self.button_reconstruction )
		self.layout_controls.addLayout( self.layout_pattern_size )
		self.layout_controls.addWidget( self.button_save_images )
		self.layout_controls.addWidget( self.button_save_mesh )
		self.layout_global = QtGui.QVBoxLayout( self )
		self.layout_global.addWidget( self.image_widget )
		self.layout_global.addLayout( self.layout_controls )
		self.layout_global.setSizeConstraint( QtGui.QLayout.SetFixedSize )
		# Set the Escape key to close the application
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Escape ), self ).activated.connect( self.close )
		# StereoSGBM
		self.disparity = sv.StereoSGBM()
		# Point cloud viewer
		self.pointcloud_viewer = sv.PointCloudViewer()
		self.X, self.Y = np.meshgrid( np.arange( 320 ), np.arange( 240 ) )
		# Initialize the USB stereo cameras
		self.stereo_camera = sv.UsbStereoCamera()
		# Lower the camera frame rate and resolution
		self.stereo_camera.camera_left.set( cv2.CAP_PROP_FRAME_WIDTH, 640 )
		self.stereo_camera.camera_left.set( cv2.CAP_PROP_FRAME_HEIGHT, 480 )
		self.stereo_camera.camera_right.set( cv2.CAP_PROP_FRAME_WIDTH, 640 )
		self.stereo_camera.camera_right.set( cv2.CAP_PROP_FRAME_HEIGHT, 480 )
		self.stereo_camera.camera_left.set( cv2.CAP_PROP_FPS, 5 )
		self.stereo_camera.camera_right.set( cv2.CAP_PROP_FPS, 5 )
		# Fix the widget size
		self.image_widget.setFixedSize( self.stereo_camera.width * 2, self.stereo_camera.height )
		# Start image acquisition
		self.stereo_camera.StartCapture(  self.ImageCallback  )
	# Receive the frame sent by the camera
	def ImageCallback( self, image_left, image_right ) :
		# Process the images
		self.update_stereo_images.emit( image_left, image_right )
	# Process the given stereo images
	def UpdateStereoImages( self, image_left, image_right ) :
		# Get the images
		self.image_left = image_left
		self.image_right = image_right
		# Copy images for display
		image_left_displayed = np.copy( self.image_left )
		image_right_displayed = np.copy( self.image_right )
		# Preview the calibration chessboard on the image
		if self.chessboard_enabled :
			image_left_displayed = sv.PreviewChessboard( image_left_displayed )
			image_right_displayed = sv.PreviewChessboard( image_right_displayed )
		# Display a cross in the middle of the image
		if self.cross_enabled :
			cv2.line( image_left_displayed, (image_left_displayed.shape[1]/2, 0), (image_left_displayed.shape[1]/2, image_left_displayed.shape[0]), (0, 0, 255), 4 )
			cv2.line( image_left_displayed, (0, image_left_displayed.shape[0]/2), (image_left_displayed.shape[1], image_left_displayed.shape[0]/2), (0, 0, 255), 4 )
			cv2.line( image_right_displayed, (image_right_displayed.shape[1]/2, 0), (image_right_displayed.shape[1]/2, image_right_displayed.shape[0]), (0, 0, 255), 4 )
			cv2.line( image_right_displayed, (0, image_right_displayed.shape[0]/2), (image_right_displayed.shape[1], image_right_displayed.shape[0]/2), (0, 0, 255), 4 )
		# Display the rectifed images
		if self.rectification_enabled and self.calibration :
			# Undistort the images according to the stereo camera calibration parameters
			rectified_images = sv.StereoRectification( self.calibration, image_left, image_right, True )
			# Prepare image for display
			stereo_image = np.concatenate( rectified_images, axis=1 )
		# Display the disparity image
		elif self.disparity_enabled and self.calibration :
			# Undistort the images according to the stereo camera calibration parameters
			rectified_images = sv.StereoRectification( self.calibration, image_left, image_right )
			rectified_images = cv2.pyrDown( rectified_images[0] ), cv2.pyrDown( rectified_images[1] )
			# Compute the disparity
			self.disparity.ComputeDisparity( *rectified_images )
			# Display the dispariy image
			stereo_image = cv2.pyrUp( self.disparity.disparity_image )
			# Point cloud
			self.coordinates = np.array( (self.X.flatten(), self.Y.flatten(), self.disparity.disparity.flatten() * 0.5) ).T
			self.coordinates = self.coordinates.reshape(-1, 3)
			self.coordinates[:,1] = -self.coordinates[:,1]
			self.colors = np.array( cv2.cvtColor( rectified_images[0], cv2.COLOR_BGR2RGB ), dtype=np.float32 ) / 255
			self.colors = self.colors.reshape(-1, 3)
			self.pointcloud_viewer.UpdatePointCloud( self.coordinates, self.colors )
		# Prepare image for display
		else : stereo_image = np.concatenate( (image_left_displayed, image_right_displayed), axis=1 )
		# Convert image color format from BGR to RGB
		stereo_image = cv2.cvtColor( stereo_image, cv2.COLOR_BGR2RGB )
		# Create a Qt image
		qimage = QtGui.QImage( stereo_image, stereo_image.shape[1], stereo_image.shape[0], QtGui.QImage.Format_RGB888 )
		# Set the image to the Qt widget
		self.image_widget.setPixmap( QtGui.QPixmap.fromImage( qimage ) )
		# Update the widget
		self.image_widget.update()
	# Toggle the chessboard preview
	def ToggleChessboard( self ) :
		self.chessboard_enabled = not self.chessboard_enabled
	# Toggle the chessboard preview
	def ToggleCross( self ) :
		self.cross_enabled = not self.cross_enabled
	# Stereo camera calibration
	def Calibration( self ) :
		self.calibration = sv.StereoCameraCalibration()
		self.button_calibration.setIcon( self.style().standardIcon( QtGui.QStyle.SP_DialogYesButton ) )
	# Image rectification
	def ToggleRectification( self ) :
		self.rectification_enabled = not self.rectification_enabled
		if self.rectification_enabled and self.button_reconstruction.isChecked() :
			self.button_reconstruction.click()
	# Disparity map
	def ToggleReconstruction( self ) :
		self.disparity_enabled = not self.disparity_enabled
		if self.disparity_enabled and self.button_rectification.isChecked() :
			self.button_rectification.click()
		if self.disparity_enabled :
			self.disparity.show()
			self.pointcloud_viewer.show()
		else :
			self.disparity.hide()
			self.pointcloud_viewer.hide()
	# Update the calibration pattern size
	def UpdatePatternSize( self, _ ) :
		sv.pattern_size = ( self.spinbox_pattern_rows.value(), self.spinbox_pattern_cols.value() )
	# Save the stereo images
	def SaveImages( self ) :
		current_time = time.strftime( '%Y%m%d_%H%M%S' )
		print( 'Save images {} to disk...'.format( current_time ) )
		if self.chessboard_enabled :
			cv2.imwrite( '{}/left-{}.png'.format( sv.calibration_directory, current_time ), self.image_left )
			cv2.imwrite( '{}/right-{}.png'.format( sv.calibration_directory, current_time ), self.image_right )
		else :
			cv2.imwrite( 'left-{}.png'.format( current_time ), self.image_left )
			cv2.imwrite( 'right-{}.png'.format( current_time ), self.image_right )
	# Save the mesh obtained from the disparity
	def SaveMesh( self ) :
		current_time = time.strftime( '%Y%m%d_%H%M%S' )
		print( 'Save point cloud {} to disk...'.format( current_time ) )
		sv.WritePly( 'stereo-{}.ply'.format( current_time ), self.coordinates, self.colors )
	# Close the widgets
	def closeEvent( self, event ) :
		# Stop image acquisition
		self.stereo_camera.StopCapture()
		# Close child widgets
		self.pointcloud_viewer.close()
		self.disparity.close()
		# Close main application
		event.accept()
