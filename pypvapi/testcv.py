import pvlib
import cv
import numpy as np
import time

if __name__ == "__main__":
    try:
        pv = pvlib.PvLib()
        cams = pv.getCameras()
        if not cams:
            print "error getting camera list"
        else:
            cam = cams[0]
            cam.startCapture()
            while True:
                frame = cam.capture()
                cv.NamedWindow('capture', 1)
                if frame.ImageSize == cam.frameSize:
                    im = np.array([ord(frame.ImageBuffer[x]) for x in range(frame.ImageSize)], dtype=np.int8)
                    print im.shape
                    im.shape = (frame.Height, frame.Width)
                    #print im
                    cv.ShowImage("capture", cv.fromarray(im))
                    cv.WaitKey(1)
                    print time.time()
                else:
                    print "Bad frame"

    finally:
        if cam:
            cam.stopCapture()

    
