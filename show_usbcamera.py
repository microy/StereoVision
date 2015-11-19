#! /usr/bin/env python
# -*- coding:utf-8 -*-

#
# Show the images from a USB camera
#

# External dependencies
import cv2
import VisionToolkit as vt

# Image callback function
def ImageCallback( image ) :
	# Display the received image
	cv2.imshow( 'USB Camera', image )
	cv2.waitKey( 1 )

# Main application
if __name__ == '__main__' :
	# Initialize the USB camera
	usbcapture = vt.UsbCapture( ImageCallback )
	# Lower the camera frame rate and resolution
	usbcapture.camera.set( cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640 )
	usbcapture.camera.set( cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480 )
	usbcapture.camera.set( cv2.cv.CV_CAP_PROP_FPS, 25 )
	# Start capture
	usbcapture.Start()
	# Wait for user key press
	raw_input( 'Press <enter> to stop the capture...' )
	# Stop image acquisition
	usbcapture.Stop()
	# Cleanup OpenCV
	cv2.destroyAllWindows()
