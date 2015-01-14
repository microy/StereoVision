#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Qt interface to display AVT cameras
#


#
# External dependencies
#
import sys
from PySide import QtCore, QtGui
import cv2
import Calibration


# Create an indexed color table (grayscale)
colortable=[]
for i in range( 256 ) : colortable.append( QtGui.qRgb( i, i , i ) )


#
# Main application to display one or two cameras
#
class CameraViewer( QtGui.QApplication ) :

	#
	# Initialisation
	#
	def __init__( self, camera_1, camera_2 = None ) :

		# Initialize parent class
		QtGui.QApplication.__init__( self, sys.argv )
		
		# Single camera viewer
		if not camera_2 : self.viewer = CameraWidget( camera_1 )
		
		# Stereo camera viewer
		else : self.viewer = StereoCameraWidget( camera_1, camera_2 )

		# Enter Qt main loop
		self.exec_()
		

#
# Widget to display a camera
#
class CameraWidget( QtGui.QWidget ) :

	# Signal send by the image callback function
	image_received = QtCore.Signal()
	do_calibration = QtCore.Signal()

	#
	# Initialisation
	#
	def __init__( self, camera ) :

		# Initialize parent class
		QtGui.QWidget.__init__( self )
		
		# Register the camera
		self.camera = camera
		
		# Set the window title
		self.setWindowTitle( 'Camera' )

		# Create a label to display camera images
		self.image_label = QtGui.QLabel( self )
		
		# Align the image to the center of the widget in both dimensions
		self.image_label.setAlignment( QtCore.Qt.AlignCenter )
				
		# Create a horizontal layout
		layout = QtGui.QHBoxLayout( self )
		
		# Add the label to display the camera
		layout.addWidget( self.image_label )
		
		# Apply the layout
		self.setLayout( layout )
		
		# Connect the OnFrameReceived signal
		self.image_received.connect( self.OnImageReceived )
		self.do_calibration.connect( self.DoCalibration )
		
		# Change the widget position and size
		self.setGeometry( 100, 100, 200, 200 )
		
		# Show the widget
		self.show()

		# Number of images saved
		self.image_count = 0
		
		# Mutex to lock the image while processing
		self.mutex = QtCore.QMutex()

		# Start image acquisition
		self.capturing = True
		self.camera.StartCapture( self.ImageCallback )
		
	#
	# Keyboard event
	#
	def keyPressEvent( self, event ) :

		# Escape
		if event.key() == QtCore.Qt.Key_Escape :
			
			# Close the application
			self.close()
			
		# Space
		elif event.key() == QtCore.Qt.Key_Space :
			
			# Lock the image data for modification
			self.mutex.lock()
			
			# Create a grayscle QImage
			qimage = QtGui.QImage( self.image.data, self.camera.width, self.camera.height, QtGui.QImage.Format_Indexed8 )

			# Unlock the image data
			self.mutex.unlock()

			# Add an indexed color table (grayscale)
			qimage.setColorTable( colortable )
			
			# Save the current image
			self.image_count += 1
			print( 'Save images {} to disk...'.format(self.image_count) )
			qimage.save( 'camera-{}-{:0>2}.png'.format(self.camera.id_string, self.image_count) )
		
	#
	# Close event
	#
	def closeEvent( self, event ) :

		# Stop image acquisition
		self.camera.StopCapture()
		
		import cv2
		cv2.destroyAllWindows()

	#
	# Incoming image from the camera
	#
	def ImageCallback( self, image ) :
	
		# Lock the image data for modification
		self.mutex.lock()
		
		# Register the incoming image
		self.image = image

		# Unlock the image data
		self.mutex.unlock()
		
		# Send a call to update the display
		self.image_received.emit()
		
		
	#
	# Display the current image
	#
	@QtCore.Slot()
	def OnImageReceived( self ) :
		
		# Lock the image data for modification
		self.mutex.lock()

		# Create a grayscle QImage
		qimage = QtGui.QImage( self.image.data, self.camera.width, self.camera.height, QtGui.QImage.Format_Indexed8 )
		
		# Unlock the image data
		self.mutex.unlock()
		
		# Add an indexed color table (grayscale)
		qimage.setColorTable( colortable )

		# Resize image for display
		qimage = qimage.scaled( self.camera.width*0.3, self.camera.height*0.3, QtCore.Qt.KeepAspectRatio )

		# Display the image
		self.image_label.setPixmap( QtGui.QPixmap.fromImage(qimage) )

		# Send a call to update the display
#		self.do_calibration.emit()

	#
	# Display the current image
	#
	@QtCore.Slot()
	def DoCalibration( self ) :

		import cv2
		# Lock the image data for modification
		self.mutex.lock()

		# Create a grayscle QImage
		local_image = cv2.resize( self.image, None, fx=0.3, fy=0.3 )
		
		# Unlock the image data
		self.mutex.unlock()
		
		# Draw calibration chessboard
		Calibration.PreviewChessboard( local_image )



#
# Window to display a camera
#
class StereoCameraWidget( QtGui.QWidget ) :

	# Signals send by the image callback function
	image_1_received = QtCore.Signal()
	image_2_received = QtCore.Signal()

	#
	# Initialisation
	#
	def __init__( self, camera_1, camera_2 ) :

		# Initialize parent class
		QtGui.QWidget.__init__( self )
		
		#  the cameras
		self.camera_1 = camera_1
		self.camera_2 = camera_2
		
		# Set the window title
		self.setWindowTitle( 'Stereo Cameras' )

		# Create two labels to display both cameras
		self.image_label_1 = QtGui.QLabel( self )
		self.image_label_2 = QtGui.QLabel( self )
		
		# Align the image to the center of the widget in both dimensions
		self.image_label_1.setAlignment( QtCore.Qt.AlignCenter )
		self.image_label_2.setAlignment( QtCore.Qt.AlignCenter )
				
		# Create a horizontal layout
		layout = QtGui.QHBoxLayout( self )
		
		# Add the two labels to display both cameras
		layout.addWidget( self.image_label_1 )
		layout.addWidget( self.image_label_2 )
				
		# Apply the layout
		self.setLayout( layout )
		
		# Connect the image received signals
		self.image_1_received.connect( self.OnImageReceived_1 )
		self.image_2_received.connect( self.OnImageReceived_2 )
		
		# Change the widget size
		self.setGeometry( 100, 100, 400, 200 )
		
		# Show the widget
		self.show()

		# Start image acquisition
		self.capturing = True
		self.camera_1.StartCapture( self.ImageCallback_1 )
		self.camera_2.StartCapture( self.ImageCallback_2 )
		
	#
	# Close event
	#
	def closeEvent( self, event ) :

		# Stop image acquisition
		self.camera_1.StopCapture()
		self.camera_2.StopCapture()

	#
	# Incoming image from the camera
	#
	def ImageCallback_1( self, image ) :
	
		# Register the incoming image
		self.image_1 = image
		
		# Send a call to update the display
		self.image_1_received.emit()
		
	#
	# Incoming image from the camera
	#
	def ImageCallback_2( self, image ) :
	
		# Register the incoming image
		self.image_2 = image
		
		# Send a call to update the display
		self.image_2_received.emit()

	#
	# Display the current image
	#
	@QtCore.Slot()
	def OnImageReceived_1( self ) :
		
		# Create a grayscle QImage
		qimage = QtGui.QImage( self.image_1.data, self.camera_1.width, self.camera_1.height, QtGui.QImage.Format_Indexed8 )
		
		# Add an indexed color table (grayscale)
		qimage.setColorTable( colortable )

		# Resize image for display
		qimage = qimage.scaled( self.camera_1.width*0.3, self.camera_1.height*0.3, QtCore.Qt.KeepAspectRatio )

		# Display the image
		self.image_label_1.setPixmap( QtGui.QPixmap.fromImage(qimage) )
		

	#
	# Display the current image
	#
	@QtCore.Slot()
	def OnImageReceived_2( self ) :
		
		# Create a grayscle QImage
		qimage = QtGui.QImage( self.image_2.data, self.camera_2.width, self.camera_2.height, QtGui.QImage.Format_Indexed8 )
		
		# Add an indexed color table (grayscale)
		qimage.setColorTable( colortable )

		# Resize image for display
		qimage = qimage.scaled( self.camera_2.width*0.3, self.camera_2.height*0.3, QtCore.Qt.KeepAspectRatio )

		# Display the image
		self.image_label_2.setPixmap( QtGui.QPixmap.fromImage(qimage) )
		
