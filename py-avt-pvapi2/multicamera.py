#
# multicamera.py
# Mikael Mannberg 2011
#
# Shows how multiple cameras can be accessed in Python.
#
# Requires OpenCV 2.3 (older versions leak memory like crazy when 
# displaying Numpy arrays)
#

import pvapi as p
import cv2
from time import sleep, time

# Initialise the driver
driver = p.PvAPI()

# Wait for cameras
print 'Waiting for cameras...'
while not driver.cameraCount():
    sleep(1)

# Grab a list of the cameras
cameraList = driver.cameraList()

# Create an empty list for the camera objects
cameras = []

# Open all cameras found on the system
for i in range(driver.cameraCount()):
	
    # Open the camera
    aCamera = p.Camera(driver, cameraList[i])

    # Print the name and id of the camera
    print aCamera.name, '(', str(aCamera.uid), ')'

    # Set the pixel format to Mono8
    aCamera.attrEnumSet('PixelFormat', 'Mono8')

    # Set the exposure time to ~ 10ms
    aCamera.attrUint32Set('ExposureValue', 10000)

    # Add it to our list of cameras
    cameras.append(aCamera)

print len(cameras), 'cameras found. Press CTRL+C to quit.'

# Wait for CTRL+C
try:
	
	# Keep going forever
    while True:
	
	    # Take an image from each camera (sequentially!) and show it
        for (camera, i) in zip(cameras, range(len(cameras))):
            image = camera.capture()
            cv2.imshow(str(i), image)

        # Let the GUI thread update
        cv2.waitKey(1)

except KeyboardInterrupt:
	
	# Close the cameras
    for camera in cameras:
        camera.close()
