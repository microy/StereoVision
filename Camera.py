#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images from two AVT Manta cameras
#


#
# External dependencies
#
from SimpleCV import AVTCamera, Display
import time

	
#
# Main
#
if __name__ == "__main__" :
	
	
	# First attached camera
	cam0 = AVTCamera()
	time.sleep(5)

	# Second attached camera
	cam1 = AVTCamera(1)
	time.sleep(5)

	
	display = Display((1280,480))
	while not display.isDone():
		img0 = cam0.getImage().resize(640,480)
		img1 = cam1.getImage().resize(640,480)
		img0.sideBySide(img1).save(display)
		time.sleep(1)
