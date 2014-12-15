#
# example.py
# Mikael Mannberg 2011
#
# Shows how a camera can be accessed in Python.
#
# Requires OpenCV 2.3 (older versions leak memory like crazy when 
# displaying Numpy arrays)
#

import pvapi as p
import cv2
from time import sleep

# Initialise the driver
driver = p.PvAPI()

# Wait for cameras
print 'Waiting for cameras...'
while not driver.cameraCount():
    sleep(1)

# Open the first camera in the list
camera = p.Camera(driver, driver.cameraList()[0])

# Set the pixel format to Bayer8
camera.attrEnumSet('PixelFormat', 'Bayer8')

# Set the exposure time to ~ 10ms
camera.attrUint32Set('ExposureValue', 10000)

print 'Showing ' + camera.name + ' (' + str(camera.uid) + '). Press CTRL+C to quit.'

# Wait for CTRL+C
try:
	
    # Keep going forever
    while True:
	
        # Capture an image
        image = camera.capture()
        # Convert it from Bayer to BGR
        image = cv2.cvtColor(image, cv2.cv.CV_BayerBG2BGR)
        cv2.imshow('Camera', image)

        # Let the GUI thread update
        cv2.waitKey(1)

except KeyboardInterrupt:
	
	# Close the camera
    camera.close()
