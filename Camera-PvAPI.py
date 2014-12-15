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
	cam1 = AVTCamera(5006506)
	time.sleep(1)

	# Second attached camera
	cam2 = AVTCamera(5009323)
	time.sleep(1)

	
	display = Display((1280,480))
	while not display.isDone():
		img1 = cam1.getImage().resize(640,480)
		img2 = cam2.getImage().resize(640,480)
		img1.sideBySide(img2).save(display)
		time.sleep(1)
