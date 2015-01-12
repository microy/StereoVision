#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Qt interface to display AVT cameras
#


#
# External dependencies
#
from PyQt4 import QtGui, QtCore


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
		
		# Backup the camera
		self.camera = camera
		
		# Set the window title
		self.setWindowTitle( 'Camera' )

		# Create a label to display camera images
		self.image_label = QtGui.QLabel( self )
		self.image_label.setScaledContents( True )
		
		# Create a dummy image to fill the label
		QImage dummy( 100, 100, QImage::Format_RGB32 )
		image = dummy
		
		# Create a layout
		layout = QtGui.QVBoxLayout( self )
		layout.addWidget( self.image_label )
		imagelabel->setPixmap( QPixmap::fromImage(image) )
		self.setLayout( layout )
		self.setGeometry( 100, 100, 200, 200 )
		self.show()
