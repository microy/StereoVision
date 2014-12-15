"""Quick example demonstrating the functionality of avt-pvapi.py"""

import numpy as np
from pvapi import *
import cv


if __name__=="__main__":

    #Initialize OpenCV Windows
    cv.NamedWindow('capture',1)
    

    #Initialize Camera Stuff
    c = CameraDriver()
    c.initialize()
    uid = c.cameraList()[0].UniqueId
    cam = c.cameraOpen(uid)

    c.captureStart(cam)
    
    #print c.attrEnumSet(cam,"AcquisitionMode","Continuous")
    c.attrEnumSet(cam,"FrameStartTriggerMode","Freerun")
    c.commandRun(cam,"AcquisitionStart")    


    #Main Capture Loop
    while True:
        frame = c.captureFrame(cam)

        imbuff = frame.ImageBuffer
        converted = [ord(imbuff[x]) for x in range(322752)]
        resized = np.array(converted).reshape(492,656)/255.0

        cv.ShowImage('capture',cv.fromarray(resized))

        if cv.WaitKey(1)==27:
            break

    #Cleanup
    c.commandRun(cam,"AcquisitionStop")
    c.captureEnd(cam)
    
    c.cameraClose(cam)
    c.attrUint32Get(cam,"StatFramesCompleted")    
    
    c.uninitialize()
