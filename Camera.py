#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images from two AVT Manta cameras
#


#
# External dependencies
#
from SimpleCV import AVTCamera, Display

	
#
# Main
#
if __name__ == "__main__" :
	
	
	# First attached camera
	cam0 = AVTCamera(0)

	# Second attached camera
	cam1 = AVTCamera(1)

	# Show a picture from the first camera
	img0 = cam0.getImage()
	img0.drawText("I am Camera ID 0")
	img0.show()

	# Show a picture from the first camera
	img1 = cam1.getImage()
	img1.drawText("I am Camera ID 1")
	img1.show()


	cam0.live()
	cam1.live()
	
	display = Display((640,240))
	while not display.isDone():
		img0 = cam0.getImage().resize(320,240)
		img1 = cam1.getImage().resize(320,240)
		img0.sideBySide(img1).save(display)
		time.sleep(5)
