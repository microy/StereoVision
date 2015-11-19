# -*- coding:utf-8 -*-

#
# Application to calibrate stereo cameras, and to recontruct a 3D scene
#

# External dependencies
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
		self.camera_widget = vt.StereoCameraWidget( self, self.calibration )
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
		self.button_reconstruction = QtGui.QPushButton( 'Reconstruction', self )
		self.button_reconstruction.setCheckable( True )
		self.button_reconstruction.setShortcut( 'F5' )
		self.button_reconstruction.clicked.connect( self.Reconstruction )
		self.spinbox_pattern_rows = QtGui.QSpinBox( self )
		self.spinbox_pattern_rows.setValue( vt.pattern_size[0] )
		self.spinbox_pattern_rows.valueChanged.connect( self.UpdatePatternSize )
		self.spinbox_pattern_cols = QtGui.QSpinBox( self )
		self.spinbox_pattern_cols.setValue( vt.pattern_size[1] )
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
		self.layout_global.addWidget( self.camera_widget )
		self.layout_global.addLayout( self.layout_controls )
		self.layout_global.setSizeConstraint( QtGui.QLayout.SetFixedSize )
		# Set the Escape key to close the application
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Escape ), self ).activated.connect( self.close )
		# Initialize the face array
		nb_lines, nb_cols = 240, 320
		vindex = np.array( range( nb_lines * nb_cols ) ).reshape( nb_lines, nb_cols )
		self.faces = np.empty( ( 2 * (nb_lines - 1) * (nb_cols - 1), 3 ), dtype=np.int )
		self.faces[ ::2, 0 ] = vindex[:nb_lines - 1, :nb_cols - 1].flatten()
		self.faces[ ::2, 1 ] = vindex[1:nb_lines, 1:nb_cols].flatten()
		self.faces[ ::2, 2 ] = vindex[:nb_lines - 1, 1:nb_cols].flatten()
		self.faces[ 1::2, 0 ] = vindex[:nb_lines - 1, :nb_cols - 1].flatten()
		self.faces[ 1::2, 1 ] = vindex[1:nb_lines, :nb_cols - 1].flatten()
		self.faces[ 1::2, 2 ] = vindex[1:nb_lines, 1:nb_cols].flatten()

	# Activate the cross on the images
	def Cross( self ) :
		self.camera_widget.cross_enabled = not self.camera_widget.cross_enabled

	# Chessboard finder
	def Chessboard( self ) :
		self.camera_widget.chessboard_enabled = not self.camera_widget.chessboard_enabled

	# Stereo camera calibration
	def Calibration( self ) :
		# Calibrate the stereo cameras
		self.calibration = vt.StereoCameraCalibration()
		self.camera_widget.calibration = self.calibration
		self.button_calibration.setIcon( self.style().standardIcon( QtGui.QStyle.SP_DialogYesButton ) )

	# Image rectification
	def Rectification( self ) :
		self.camera_widget.rectification_enabled = not self.camera_widget.rectification_enabled
		if self.camera_widget.rectification_enabled and self.button_reconstruction.isChecked() :
			self.button_reconstruction.click()

	# Disparity map
	def Reconstruction( self ) :
		self.camera_widget.disparity_enabled = not self.camera_widget.disparity_enabled
		if self.camera_widget.disparity_enabled and self.button_rectification.isChecked() :
			self.button_rectification.click()
		if self.camera_widget.disparity_enabled :
			self.camera_widget.disparity.show()
			self.camera_widget.pointcloud_viewer.show()
		else :
			self.camera_widget.disparity.hide()
			self.camera_widget.pointcloud_viewer.hide()

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

	# Save the mesh obtained from the disparity
	def SaveMesh( self ) :
		vt.WritePly( 'stereo.ply', self.camera_widget.coordinates, self.camera_widget.colors )

	# Close the camera widget
	def closeEvent( self, event ) :
		# Stop image acquisition, and close the widgets
		self.camera_widget.close()
		event.accept()

# Stereovision user interface
class StereoVisionNew( QtGui.QWidget ) :

	# Signal sent to update the image in the widget
	update_image = QtCore.Signal( np.ndarray )

	# Initialization
	def __init__( self, parent = None ) :
		# Initialise QWidget
		super( StereoVisionNew, self ).__init__( parent )
		# Load the calibration parameter file, if it exists
		self.calibration = vt.LoadCalibration()
		if not self.calibration : vt.CreateCalibrationDirectory()
		# Initialize the viewing parameters
		self.chessboard_enabled = False
		self.cross_enabled = False
		self.rectification_enabled = False
		self.disparity_enabled = False
		# Set the window title
		self.setWindowTitle( 'StereoVision' )
		# Connect the signal to update the image
		self.update_image.connect( self.UpdateImage )
		# Widget to display the images from the cameras
		self.image_widget = QtGui.QLabel( self )
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
		self.spinbox_pattern_rows.setValue( vt.pattern_size[0] )
		self.spinbox_pattern_rows.valueChanged.connect( self.UpdatePatternSize )
		self.spinbox_pattern_cols = QtGui.QSpinBox( self )
		self.spinbox_pattern_cols.setValue( vt.pattern_size[1] )
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
		self.disparity = vt.StereoSGBM()
		# Point cloud viewer
		self.pointcloud_viewer = vt.PointCloudViewer()

	# Process the given stereo images
	def ProcessStereoImages( self, image_left, image_right ) :
		# Get the images
		self.image_left = image_left
		self.image_right = image_right
		# Copy images for display
		image_left_displayed = np.copy( self.image_left )
		image_right_displayed = np.copy( self.image_right )
		# Preview the calibration chessboard on the image
		if self.chessboard_enabled :
			image_left_displayed = vt.PreviewChessboard( image_left_displayed )
			image_right_displayed = vt.PreviewChessboard( image_right_displayed )
		# Display a cross in the middle of the image
		if self.cross_enabled :
			cv2.line( image_left_displayed, (image_left_displayed.shape[1]/2, 0), (image_left_displayed.shape[1]/2, image_left_displayed.shape[0]), (0, 0, 255), 4 )
			cv2.line( image_left_displayed, (0, image_left_displayed.shape[0]/2), (image_left_displayed.shape[1], image_left_displayed.shape[0]/2), (0, 0, 255), 4 )
			cv2.line( image_right_displayed, (image_right_displayed.shape[1]/2, 0), (image_right_displayed.shape[1]/2, image_right_displayed.shape[0]), (0, 0, 255), 4 )
			cv2.line( image_right_displayed, (0, image_right_displayed.shape[0]/2), (image_right_displayed.shape[1], image_right_displayed.shape[0]/2), (0, 0, 255), 4 )
		# Display the rectifed images
		if self.rectification_enabled and self.calibration :
			# Undistort the images according to the stereo camera calibration parameters
			rectified_images = vt.StereoRectification( self.calibration, image_left, image_right, True )
			# Prepare image for display
			stereo_image = np.concatenate( rectified_images, axis=1 )
		# Display the disparity image
		elif self.disparity_enabled and self.calibration :
			# Undistort the images according to the stereo camera calibration parameters
			rectified_images = vt.StereoRectification( self.calibration, image_left, image_right )
			rectified_images = cv2.pyrDown( rectified_images[0] ), cv2.pyrDown( rectified_images[1] )
			# Compute the disparity
			self.disparity.ComputeDisparity( *rectified_images )
			# Display the dispariy image
			stereo_image = cv2.pyrUp( self.disparity.disparity_image )
			# Point cloud
			self.coordinates = np.array( (self.X.flatten(), self.Y.flatten(), self.disparity.disparity.flatten() * 0.5) ).T
			self.coordinates = self.coordinates.reshape(-1, 3)
			self.coordinates[:,1] = -self.coordinates[:,1]
			self.colors = np.array( cv2.cvtColor( rectified_images[0], cv2.COLOR_GRAY2RGB ), dtype=np.float32 ) / 255
			self.colors = self.colors.reshape(-1, 3)
			self.pointcloud_viewer.update_pointcloud.emit( self.coordinates, self.colors )
		# Or display the stereo images
		else :
			# Prepare image for display
			stereo_image = np.concatenate( (image_left_displayed, image_right_displayed), axis=1 )
		# Send the image to the widget through a signal
		self.update_image.emit( stereo_image )

	# Update the image in the widget
	def UpdateImage( self, image ) :
		# Create a Qt image
		qimage = QtGui.QImage( image, image.shape[1], image.shape[0], QtGui.QImage.Format_RGB888 )
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
		# Calibrate the stereo cameras
		self.calibration = vt.StereoCameraCalibration()
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
		# Get the calibration pattern dimensions
		vt.pattern_size = ( self.spinbox_pattern_rows.value(), self.spinbox_pattern_cols.value() )

	# Save the stereo images
	def SaveImages( self ) :
		# Save images to disk
		current_time = time.strftime( '%Y%m%d_%H%M%S' )
		print( 'Save images {} to disk...'.format( current_time ) )
		if self.chessboard_enabled :
			cv2.imwrite( '{}/left-{}.png'.format( vt.calibration_directory, current_time ), self.image_left )
			cv2.imwrite( '{}/right-{}.png'.format( vt.calibration_directory, current_time ), self.image_right )
		else :
			cv2.imwrite( 'left-{}.png'.format( current_time ), self.image_left )
			cv2.imwrite( 'right-{}.png'.format( current_time ), self.image_right )

	# Save the mesh obtained from the disparity
	def SaveMesh( self ) :
		# Save images to disk
		current_time = time.strftime( '%Y%m%d_%H%M%S' )
		print( 'Save point cloud {} to disk...'.format( current_time ) )
		vt.WritePly( 'stereo-{}.ply'.format( current_time ), self.coordinates, self.colors )

	# Close the camera widget
	def closeEvent( self, event ) :
		# Close the widgets
		self.pointcloud_viewer.close()
		self.disparity.close()
		event.accept()

# Stereovision user interface for Allied Vision cameras
class VmbStereoVisionNew( StereoVisionNew ) :

	# Initialization
	def __init__( self, parent = None ) :
		# Initialise QWidget
		super( VmbStereoVisionNew, self ).__init__( parent )
		# Initialize the Vimba driver
		vt.VmbStartup()
		# Initialize the stereo cameras
		self.camera = vt.VmbStereoCamera( '50-0503326223', '50-0503323406' )
		# Connect the cameras
		self.camera.Open()
		# Fix the widget size
		self.image_widget.setFixedSize( self.camera.camera_left.width, self.camera.camera_left.height/2 )
		self.image_widget.setScaledContents( True )
		# Start image acquisition
		self.camera.StartCapture( self.FrameCallback )

	# Receive the frame sent by the camera
	def FrameCallback( self, frame_left, frame_right ) :
		# Check frame status
		if not frame_left.is_valid or not frame_right.is_valid : return
		# Get the images
		image_left = cv2.cvtColor( frame_left.image, cv2.COLOR_GRAY2RGB )
		image_right = cv2.cvtColor( frame_right.image, cv2.COLOR_GRAY2RGB )
		# Process the images
		self.ProcessStereoImages( image_left, image_right )

	# Close the camera widget
	def closeEvent( self, event ) :
		# Stop image acquisition
		self.camera.StopCapture()
		# Disconnect the camera
		self.camera.Close()
		# Shutdown Vimba
		vt.VmbShutdown()
		# Close the widgets
		super( VmbStereoVisionNew, self ).closeEvent( event )
