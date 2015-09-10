# -*- coding:utf-8 -*- 


#
# Qt interface for the disparity module
#


#
# External dependencies
#
import pickle
import sys
import cv2
import numpy as np
import PySide.QtCore as qtcore
import PySide.QtGui as qtgui



#
# Main application to display a mesh
#
class QtDisparity( qtgui.QApplication ) :

	#
	# Initialisation
	#
	def __init__( self ) :

		# Initialize parent class
		super( QtDisparity, self ).__init__( sys.argv )
		
		# Show the widget used to display the mesh
		self.qtstereobmwidget = QtStereoBM()
		self.qtstereobmwidget.show()
		
		# Enter Qt main loop
		self.exec_()



#
# Customize the Qt widget to setup the stereo BM
#
class QtStereoBM( qtgui.QWidget ) :

	#
	# Initialisation
	#
	def __init__( self, parent = None ) :
		
		#
		# Initialize the StereoBM
		#
		
		# Load stereo calibration parameter file
		with open( 'stereo-calibration.pkl' , 'rb') as input_file :
			calibration = pickle.load( input_file )

		# Read the images
		self.left_image = cv2.imread( 'left.png', cv2.CV_LOAD_IMAGE_GRAYSCALE )
		self.right_image = cv2.imread( 'right.png', cv2.CV_LOAD_IMAGE_GRAYSCALE )

		# Remap the images
		self.left_image = cv2.remap( self.left_image, calibration['left_map'][0], calibration['left_map'][1], cv2.INTER_LINEAR )
		self.right_image = cv2.remap( self.right_image, calibration['right_map'][0], calibration['right_map'][1], cv2.INTER_LINEAR )

		# StereoBM parameters
		self.preset = cv2.STEREO_BM_BASIC_PRESET
		self.ndisparities = 48
		self.SADWindowSize = 9

		#
		# Initialize the interface
		#

		# Initialise QWidget
		super( QtStereoBM, self ).__init__( parent )

		# Set the window title
		self.setWindowTitle( 'StereoBM disparity' )

		# Set the window size
		self.setGeometry( qtcore.QRect(10, 10, 521, 151) )

		# Number of disparities control
		self.slider_disparities = qtgui.QSlider( self )
		self.slider_disparities.setOrientation( qtcore.Qt.Horizontal )
		self.slider_disparities.setValue( self.ndisparities )
		self.slider_disparities.setTickInterval( 16 )
		self.slider_disparities.setMaximum( 240 )
		self.slider_disparities.valueChanged.connect( self.Setndisparities )
		self.label_disparities = qtgui.QLabel( self )
		self.label_disparities.setText( 'Number of disparities' )
		self.label_disparities_value = qtgui.QLabel( self )
		self.label_disparities_value.setText( '{}'.format( self.ndisparities ) )

		# SAD window size control
		self.slider_sad_window = qtgui.QSlider( self )
		self.slider_sad_window.setOrientation( qtcore.Qt.Horizontal )
		self.slider_sad_window.setValue( self.SADWindowSize )
		self.slider_sad_window.setMinimum( 5 )
		self.slider_sad_window.setMaximum( 255 )
		self.slider_sad_window.valueChanged.connect( self.SetSADWindowSize )
		self.label_sad_window = qtgui.QLabel( self )
		self.label_sad_window.setText( 'SAD Window size' )
		self.label_sad_window_value = qtgui.QLabel( self )
		self.label_sad_window_value.setText( '{}'.format( self.SADWindowSize ) )

		# Apply button
		self.button_apply = qtgui.QDialogButtonBox( self )
		self.button_apply.setStandardButtons( qtgui.QDialogButtonBox.Apply )
		self.button_apply.setCenterButtons( True )
		self.button_apply.clicked.connect( self.UpdateDisparity )

		# Widget layout
		self.layout_grid = qtgui.QGridLayout()
		self.layout_grid.addWidget( self.label_disparities, 0, 0 )
		self.layout_grid.addWidget( self.slider_disparities, 0, 1 )
		self.layout_grid.addWidget( self.label_disparities_value, 0, 2 )
		self.layout_grid.addWidget( self.label_sad_window, 1, 0 )
		self.layout_grid.addWidget( self.slider_sad_window, 1, 1 )
		self.layout_grid.addWidget( self.label_sad_window_value, 1, 2 )
		self.layout_vertical = qtgui.QVBoxLayout( self )
		self.layout_vertical.addLayout( self.layout_grid )
		self.layout_vertical.addWidget( self.button_apply )
		
	#
	# Set the number ot disparities (multiple of 16)
	#
	def Setndisparities( self, value ) :
		if value % 16 :	value -= value % 16
		self.ndisparities = value
		self.slider_disparities.setValue( value )
		self.label_disparities_value.setText( '{}'.format( value ) )

	#
	# Set the search window size (odd, and in range [5...255])
	#
	def SetSADWindowSize( self, value ) :
		if value < 5 : value = 5
		elif not value % 2 : value += 1
		self.SADWindowSize = value
		self.slider_sad_window.setValue( value )
		self.label_sad_window_value.setText( '{}'.format( value ) )

	#
	# Compute the stereo correspondence
	#
	def UpdateDisparity( self ):
		
		self.bm = cv2.StereoBM( self.preset, self.ndisparities, self.SADWindowSize )
		self.bm_disparity = self.bm.compute( self.left_image, self.right_image, disptype=cv2.CV_32F )
		self.bm_disparity_img = self.bm_disparity * 255.99 / ( self.bm_disparity.min() - self.bm_disparity.max() )
		self.bm_disparity_img = self.bm_disparity_img.astype( np.uint8 )
	#	self.bm_disparity_img = cv2.applyColorMap( self.bm_disparity_img, cv2.COLORMAP_JET )
		cv2.imshow( 'Disparity map', cv2.pyrDown( self.bm_disparity_img ) )
		cv2.waitKey( 1 )

