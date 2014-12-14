import pvlib
import cv2
import time

if __name__ == "__main__":
    cam = None
    pv = pvlib.PvLib()
    cams = pv.getCameras()
    if not cams:
        print "error getting camera list"
    else:
        cam = cams[0]
        cv2.namedWindow('capture')
        cam.startCaptureTrigger()
        while True:
            frame = cam.getNumpyArray()
            cv2.imshow("capture", frame)
            cv2.waitKey(100)
            print time.time()
        cam.stopCapture()

    
