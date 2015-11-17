# -*- coding:utf-8 -*-


#
# Module to display live images from a camera
#


#
# External dependencies
#
import cv2
import numpy as np
from PySide import QtCore
from PySide import QtGui
import VisionToolkit as vt


#
# Qt Widget to display the images from a camera
#
class CameraWidget( QtGui.QLabel ) :

	#
	# Signal sent to update the image in the widget
	#
	update_image = QtCore.Signal( np.ndarray )

	#
	# Initialization
	#
	def __init__( self, parent = None ) :

		# Initialize QLabel
		super( CameraWidget, self ).__init__( parent )

		# Connect the signal to update the image
		self.update_image.connect( self.UpdateImage )

	#
	# Update the image in the widget
	#
	def UpdateImage( self, image ) :

		# Create a Qt image
		qimage = QtGui.QImage( image, image.shape[1], image.shape[0], QtGui.QImage.Format_RGB888 )

		# Set the image to the Qt widget
		self.setPixmap( QtGui.QPixmap.fromImage( qimage ) )

		# Update the widget
		self.update()


#
# Qt Widget to display the images from a USB camera
#
class UsbCameraWidget( CameraWidget ) :

	#
	# Initialization
	#
	def __init__( self, parent = None ) :

		# Initialize the camera widget
		super( UsbCameraWidget, self ).__init__( parent )

		# Change the window title
		self.setWindowTitle( 'USB Camera' )

		# Fix the widget size
		self.setFixedSize( 640, 480 )
		self.setScaledContents( True )

		# Set the Escape key to close the application
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Escape ), self ).activated.connect( self.close )

		# Initialize the camera
		self.camera = vt.UsbCamera( self.ProcessImage )
		self.camera.start()

	#
	# Process the image from the camera
	#
	def ProcessImage( self, image ) :

		# Convert color coding
		image = cv2.cvtColor( image, cv2.COLOR_BGR2RGB )

		# Update the image in the widget
		self.update_image.emit( image )

	#
	# Close the camera viewer
	#
	def closeEvent( self, event ) :

		# Stop image acquisition
		self.camera.running = False
		self.camera.join()

		# Close the widget
		event.accept()


#
# Qt Widget to display the images from an Allied Vision camera (through Vimba)
#
class VmbCameraWidget( CameraWidget ) :

	#
	# Initialization
	#
	def __init__( self, camera_id, parent = None ) :

		# Initialize the camera widget
		super( VmbCameraWidget, self ).__init__( parent )

		# Change the window title
		self.setWindowTitle( 'Allied Vision Camera' )

		# Fix the widget size
		self.setFixedSize( 2452*0.3, 2056*0.3 )
		self.setScaledContents( True )

		# Set the Escape key to close the application
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Escape ), self ).activated.connect( self.close )

		# Initialize the Vimba driver
		vt.VmbStartup()

		# Initialize the camera
		self.camera = vt.VmbCamera( camera_id )

		# Connect the camera
		self.camera.Open()

		# Start image acquisition
		self.camera.StartCapture( self.FrameCallback )

	#
	# Receive the frame sent by the camera
	#
	def FrameCallback( self, frame ) :

		# Check frame status
		if not frame.is_valid : return

		# Convert the frame and its color coding
		image = cv2.cvtColor( frame.image, cv2.COLOR_GRAY2RGB )

		# Send the image to the widget through a signal
		self.update_image.emit( image )

	#
	# Close the camera viewer
	#
	def closeEvent( self, event ) :

		# Stop image acquisition
		self.camera.StopCapture()

		# Disconnect the camera
		self.camera.Close()

		# Shutdown Vimba
		vt.VmbShutdown()

		# Close the widget
		event.accept()

#
# Qt Widget to display the images from two Allied Vision cameras (through Vimba)
#
class VmbStereoCameraWidget( QtGui.QLabel ) :

	#
	# Signal sent to update the image in the widget
	#
	update_image = QtCore.Signal()

	#
	# Initialization
	#
	def __init__( self, camera_left_id, camera_right_id, parent = None ) :

		# Initialize the camera widget
		super( VmbStereoCameraWidget, self ).__init__( parent )

		# Connect the signal to update the image
		self.update_image.connect( self.UpdateImage )

		# Change the window title
		self.setWindowTitle( 'Allied Vision Stereo Camera' )

		# Fix the widget size
		self.setFixedSize( 2452*0.5, 2056*0.25 )
		self.setScaledContents( True )

		# Initialize the viewing parameters
		self.chessboard_enabled = False
		self.cross_enabled = False

		# Set the Escape key to close the application
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Escape ), self ).activated.connect( self.close )

		# Set the Space key to toggle the chessboard preview
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Space ), self ).activated.connect( self.ToggleChessboard )

		# Set the Space key to toggle the cross preview
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_C ), self ).activated.connect( self.ToggleCross )

		# Initialize the Vimba driver
		vt.VmbStartup()

		# Initialize the stereo cameras
		self.camera = vt.VmbStereoCamera( camera_left_id, camera_right_id )

		# Connect the cameras
		self.camera.Open()

		# Start image acquisition
		self.camera.StartCapture( self.FrameCallback )

	#
	# Receive the frame sent by the camera
	#
	def FrameCallback( self, frame_left, frame_right ) :


		# Copy images for display
		self.image_left = frame_left.image
		self.image_right = frame_right.image

		# Send the image to the widget through a signal
		self.update_image.emit()

	#
	# Update the image in the widget
	#
	def UpdateImage( self ) :

		# Prepare image for display
	#	stereo_image = np.concatenate( ( self.image_left, self.image_right ), axis=1 )
	#	stereo_image = cv2.cvtColor( stereo_image, cv2.COLOR_GRAY2RGB )

		# Create a Qt image
	#	qimage = QtGui.QImage( stereo_image, stereo_image.shape[1], stereo_image.shape[0], QtGui.QImage.Format_RGB888 )

		# Set the image to the Qt widget
	#	self.setPixmap( QtGui.QPixmap.fromImage( qimage ) )

		# Update the widget
		self.update()

	#
	# Toggle the chessboard preview
	#
	def ToggleChessboard( self ) :

		self.chessboard_enabled = not self.chessboard_enabled

	#
	# Toggle the chessboard preview
	#
	def ToggleCross( self ) :

		self.cross_enabled = not self.cross_enabled

	#
	# Close the camera viewer
	#
	def closeEvent( self, event ) :

		# Stop image acquisition
		self.camera.StopCapture()

		# Disconnect the camera
		self.camera.Close()

		# Shutdown Vimba
		vt.VmbShutdown()

		# Close the widget
		event.accept()
