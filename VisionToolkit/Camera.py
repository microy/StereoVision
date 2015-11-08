# -*- coding:utf-8 -*-


#
# Module to display live images from a camera
#


#
# External dependencies
#
import threading
import numpy as np
import cv2
from PySide import QtCore
from PySide import QtGui
import Vimba


#
# Qt Widget to display the images from an Allied Vision camera (through Vimba)
#
class VmbCameraWidget( QtGui.QLabel ) :

	#
	# Signal sent by the image callback function called by Vimba
	#
	update_image = QtCore.Signal( np.ndarray )

	#
	# Initialization
	#
	def __init__( self, camera_id, parent = None ) :

		# Initialize QLabel
		super( VmbCameraWidget, self ).__init__( parent )

		# Change the window title
		self.setWindowTitle( 'Allied Vision Camera' )

		# Fix the widget size
		self.setFixedSize( 2452*0.3, 2056*0.3 )
		self.setScaledContents( True )

		# Set the Escape key to close the application
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Escape ), self ).activated.connect( self.close )

		# Connect the signal to update the image
		self.update_image.connect( self.UpdateImage )

		# Initialize the Vimba driver
		Vimba.VmbStartup()

		# Initialize the camera
		self.camera = Vimba.VmbCamera( camera_id )

		# Connect the camera
		self.camera.Open()

		# Start image acquisition
		self.camera.StartCapture( self.ImageCallback )

	#
	# Receive the image sent by the camera
	#
	def ImageCallback( self, image ) :

		# Convert color coding
		image = cv2.cvtColor( image, cv2.COLOR_GRAY2RGB )

		# Send the image to the widget through a signal
		self.update_image.emit( image )

	#
	# Display the image from the camera
	#
	def UpdateImage( self, image ) :

		# Create a Qt image
		qimage = QtGui.QImage( image, image.shape[1], image.shape[0], QtGui.QImage.Format_RGB888 )

		# Set the image to the Qt widget
		self.setPixmap( QtGui.QPixmap.fromImage( qimage ) )

		# Update the widget
		self.update()

	#
	# Close the camera viewer
	#
	def closeEvent( self, event ) :

		# Stop image acquisition
		self.camera.StopCapture()

		# Disconnect the camera
		self.camera.Close()

		# Shutdown Vimba
		Vimba.VmbShutdown()

		# Accept the Qt close event
		event.accept()


#
# Thread to read images from a USB camera
#
class UsbCamera( threading.Thread ) :

	#
	# Initialisation
	#
	def __init__( self, image_callback ) :

		# Initialize the thread
		super( UsbCamera, self ).__init__()

		# Function called when an image is received
		self.image_callback = image_callback

		# Initialize the camera
		self.camera = cv2.VideoCapture( 0 )

		# Set camera resolution
		self.camera.set( cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640 )
		self.camera.set( cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480 )

		# Set camera frame rate
		self.camera.set( cv2.cv.CV_CAP_PROP_FPS, 25 )

	#
	# Thread main loop
	#
	def run( self ) :

		# Thread running
		self.running = True
		while self.running :

			# Capture image from the camera
			_, image = self.camera.read()

			# Send the image via the external callback function
			self.image_callback( image )

		# Release the camera
		self.camera.release()


#
# Qt Widget to display the images from a USB camera
#
class UsbCameraWidget( QtGui.QLabel ) :

	#
	# Signal sent to update the image in the widget
	#
	update_image = QtCore.Signal( np.ndarray )

	#
	# Initialization
	#
	def __init__( self, parent = None ) :

		# Initialize QLabel
		super( UsbCameraWidget, self ).__init__( parent )

		# Change the window title
		self.setWindowTitle( 'USB Camera' )

		# Fix the widget size
		self.setFixedSize( 640, 480 )
		self.setScaledContents( True )

		# Set the Escape key to close the application
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Escape ), self ).activated.connect( self.close )

		# Connect the signal to update the image
		self.update_image.connect( self.UpdateImage )

		# Initialize the stereo cameras
		self.camera = UsbCamera( self.ProcessImage )
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
	# Display the image
	#
	def UpdateImage( self, image ) :

		# Create a Qt image
		qimage = QtGui.QImage( image, image.shape[1], image.shape[0], QtGui.QImage.Format_RGB888 )

		# Set the image to the Qt widget
		self.setPixmap( QtGui.QPixmap.fromImage( qimage ) )

		# Update the widget
		self.update()

	#
	# Close the camera viewer
	#
	def closeEvent( self, event ) :

		# Stop image acquisition
		self.camera.running = False
		self.camera.join()

		# Close the widget
		event.accept()
