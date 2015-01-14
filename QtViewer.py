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
		
#		self.image_label.setScaledContents( True )

		# Align the image to the center of the widget in both dimensions
		self.image_label.setAlignment( QtCore.Qt.AlignCenter )
		
#		import cv2
#		img = cv2.imread('examples/cam1-01.png')
#		print( img.shape )
		
		# Create a dummy image to fill the label
#		image = QtGui.QImage( img.data, camera.width, camera.height, QtGui.QImage.Format_Indexed8 )
#		COLORTABLE=[]
#		for i in range( 256 ) : COLORTABLE.append( QtGui.qRgb( i, i , i ) )
#		image.setColorTable(COLORTABLE)

		image = QtGui.QImage( 'examples/camera1-02.png' )
		
		# Create a color table
		image.setColorCount( 256 )
		for i in range( 256 ) : image.setColor( i, QtGui.qRgb( i, i , i ) )
		
		print( image.format(), image.width(), image.height() )
		image = image.scaled( image.width()*0.3, image.height()*0.3, QtCore.Qt.KeepAspectRatio )
		print( image.format(), image.width(), image.height(), image.colorTable() )
		
		# Create a horizontal layout
		layout = QtGui.QHBoxLayout( self )
		
		# Add the label to display the camera
		layout.addWidget( self.image_label )
		
		# Display the image in the label
		self.image_label.setPixmap( QtGui.QPixmap.fromImage(image) )
		
		# Apply the layout
		self.setLayout( layout )
		
		# Change the widget position and size
		self.setGeometry( 100, 100, 200, 200 )
		
		# Show the widget
		self.show()

		# Start image acquisition
		self.capturing = True
		self.camera.StartCapture( self.ImageCallback )
		
	#
	# Close event
	#
	def closeEvent( self, event ) :

		# Stop image acquisition
		self.camera.StopCapture()

	#
	# Display the current image
	#
	def ImageCallback( self, image ) :
		
		# Create a qimage
		qimage = QtGui.QImage( image.data, self.camera.width, self.camera.height, QtGui.QImage.Format_Indexed8 )

		# Resize image for display
		qimage = image.scaled( self.camera.width*0.3, self.camera.height*0.3, QtCore.Qt.KeepAspectRatio )

		# Display the image
		self.image_label.setPixmap( QtGui.QPixmap.fromImage(qimage) )


#
# Window to display a camera
#
class StereoCameraWidget( QtGui.QWidget ) :

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

		# Create a label to display camera 1
		self.image_label_1 = QtGui.QLabel( self )
		self.image_label_1.setScaledContents( True )

		# Create a label to display camera 2
		self.image_label_2 = QtGui.QLabel( self )
		self.image_label_2.setScaledContents( True )
		
		# Create a dummy image to fill the label
		image = QtGui.QImage( 100, 100, QtGui.QImage.Format_RGB32 )
		
		# Create a horizontal layout
		layout = QtGui.QHBoxLayout( self )
		
		# Add the two labels to display both cameras
		layout.addWidget( self.image_label_1 )
		layout.addWidget( self.image_label_2 )
		
		# Add dummy image
		self.image_label_1.setPixmap( QtGui.QPixmap.fromImage(image) )
		self.image_label_2.setPixmap( QtGui.QPixmap.fromImage(image) )
		
		# Apply the layout
		self.setLayout( layout )
		
		# Change the widget size
		self.setGeometry( 100, 100, 400, 200 )
		
		# Show the widget
		self.show()
