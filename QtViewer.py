#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Qt interface to display AVT cameras
#


#
# External dependencies
#
from PySide import QtGui


#
# Window to display a camera
#
class QtViewer( QtGui.QWidget ) :

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
		self.image_label.setScaledContents( True )
		
		# Create a dummy image to fill the label
		image = QtGui.QImage( 100, 100, QtGui.QImage.Format_RGB32 )
		
		# Create a horizontal layout
		layout = QtGui.QHBoxLayout( self )
		
		# Add the label to display the camera
		layout.addWidget( self.image_label )
		
		# Add dummy image
		self.image_label.setPixmap( QtGui.QPixmap.fromImage(image) )
		
		# Apply the layout
		self.setLayout( layout )
		
		# Change the widget size
		self.setGeometry( 100, 100, 200, 200 )
		
		# Show the widget
		self.show()


#
# Window to display a camera
#
class QtStereoViewer( QtGui.QWidget ) :

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
