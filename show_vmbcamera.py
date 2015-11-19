#! /usr/bin/env python
# -*- coding:utf-8 -*-

#
# Show the images from an Allied Vision camera
#

# External dependencies
import cv2
import VisionToolkit as vt

# Function called by the camera when images are received
def FrameCallback( frame ) :
	# Check frame status
	if not frame.is_valid : return
	# Display the stereo image
	cv2.imshow( 'Allied Vision Camera', frame.image )
	cv2.waitKey( 1 )

# Main application
if __name__ == '__main__' :
	# Initialize the Vimba driver
	vt.VmbStartup()
	# Initialize the camera
	camera = vt.VmbCamera( '50-0503326223' )
#	camera = vt.VmbCamera( '50-0503323406' )
	# Connect the camera
	camera.Open()
	# Start image acquisition
	camera.StartCapture( FrameCallback )
	# Wait for user key press
	raw_input( 'Press enter to stop the capture...' )
	# Stop image acquisition
	camera.StopCapture()
	# Disconnect the camera
	camera.Close()
	# Shutdown Vimba
	vt.VmbShutdown()
	# Cleanup OpenCV
	cv2.destroyAllWindows()
