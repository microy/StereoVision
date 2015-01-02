#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images synchronously
# from two AVT Manta cameras with the Vimba SDK
#


# External dependencies
import collections, cv2, time
import Vimba

# Number of images saved
image_count = 0

# Frame per second counter
counter = 0
fps_counter = 0
fps_buffer = collections.deque( 10*[0], 10 )

# Vimba initialization
print( 'Vimba initialization...' )
vimba = Vimba.VmbSystem()
vimba.Startup()

# Camera connection
print( 'Camera connection...' )
camera = Vimba.VmbCamera( vimba )
camera.Connect( '50-0503323406' )

# Start image acquisition
print( 'Start acquisition...' )
camera.CaptureStart()

# Live display
while True :
	
	# Initialize the clock for counting the number of frames per second
	time_start = time.clock()

	# Capture an image
	camera.CaptureFrame()
	
	# Resize image for display
	image_final = cv2.resize( camera.image, None, fx=0.3, fy=0.3 )

	# Display the image (scaled down)
	cv2.imshow( "Camera", image_final )
	
	# Keyboard interruption
	key = cv2.waitKey(1) & 0xFF
	
	# Escape key
	if key == 27 :
		
		# Exit live display
		break
		
	# Space key
	elif key == 32 :
		
		# Save images to disk 
		image_count += 1
		print( 'Save image {} to disk...'.format( image_count ) )
		cv2.imwrite( 'camera-{:0>2}.png'.format(image_count), camera.image )
		
	# Frames per second counter
	fps_buffer.pop()
	fps_buffer.appendleft( time.clock() - time_start )
	fps_counter = 10.0 / sum( fps_buffer )
	counter += 1
	if counter == 20 :
		print( '{:.2f} FPS'.format( fps_counter ) )
		counter = 0

# Cleanup OpenCV
cv2.destroyAllWindows()

# Stop image acquisition
print( 'Stop acquisition...' )
camera.CaptureStop()

# Camera disconnection
print( 'Camera disconnection...' )
camera.Disconnect()

# Vimba shutdown
print( 'Vimba shutdown...' )
vimba.Shutdown()
