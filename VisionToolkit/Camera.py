# -*- coding:utf-8 -*- 


#
# Module to display live images from a camera
#


#
# External dependencies
#
import ctypes as ct
import sys
import numpy as np
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
	image_received = QtCore.Signal( np.ndarray )

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
		self.image_received.connect( self.UpdateImage )
		
		# Create an indexed color table (grayscale)
		self.colortable = [ QtGui.qRgb( i, i, i ) for i in range( 256 ) ]
		
		# Initialize the Vimba driver
		Vimba.VmbStartup()

		# Initialize the camera
		self.camera = Vimba.VmbCamera( camera_id )
		
		# Connect the camera
		self.camera.Open()

		# Configure the sync out signal
		Vimba.vimba.VmbFeatureEnumSet( self.camera.handle, 'SyncOutSource', 'Exposing' )

		# Configure fixed rate trigger
		Vimba.vimba.VmbFeatureEnumSet( self.camera.handle, 'TriggerSource', 'FixedRate' )
		Vimba.vimba.VmbFeatureFloatSet( self.camera.handle, 'AcquisitionFrameRateAbs', ct.c_double( 7.4 ) )
	
		# Start image acquisition
		self.camera.StartCapture( self.FrameCallback )

	#
	# Receive the image sent by the camera
	#
	def FrameCallback( self, frame ) :
		
		# Send the image to the widget through a signal
		self.image_received.emit( frame.image )
		
	#
	# Display the image from the camera
	#
	def UpdateImage( self, image ) :
		
		# Create a Qt image
		qimage = QtGui.QImage( image, image.shape[1], image.shape[0], QtGui.QImage.Format_Indexed8 )
		
		# Add an indexed color table (grayscale)
		qimage.setColorTable( self.colortable )
			
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
		
		# Restore camera default parameters
		Vimba.vimba.VmbFeatureEnumSet( self.camera.handle, 'UserSetSelector', 'Default' )
		Vimba.vimba.VmbFeatureCommandRun( self.camera.handle, 'UserSetLoad' )
		
		# Disconnect the camera
		self.camera.Close()

		# Shutdown Vimba
		Vimba.VmbShutdown()
		
		# Accept the Qt close event
		event.accept()


#
# Main application
#
if __name__ == '__main__' :

	application = QtGui.QApplication( sys.argv )
	widget = VmbCameraWidget( '50-0503326223' )
	widget.show()
	sys.exit( application.exec_() )

