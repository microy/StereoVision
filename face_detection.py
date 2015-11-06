#! /usr/bin/env python
# -*- coding:utf-8 -*-


#
# Application to detect faces in real-time with a webcam
#


#
# External dependencies
#
import sys
import time
import threading
import cv2
import numpy as np
from PySide import QtGui
import VisionToolkit as vtk


#
# Thread to detect the faces on an image
#
class FaceDetection( threading.Thread ) :

    #
    # Initialization
    #
    def __init__( self, image_callback ) :

        # Initialize the thread
        super( FaceDetection, self ).__init__()

        # Function called when the image is processed
        self.image_callback = image_callback

        # Image to be processed
        self.image = None

        # Face detector
        self.face_cascade = cv2.CascadeClassifier( 'haarcascade_frontalface_default.xml' )

    #
    # Thread main loop
    #
    def run( self ) :

        # Thread running
        self.running = True
        while self.running :

            # Wait for an image to process
            if not isinstance( self.image, np.ndarray ) :
                time.sleep( 0.1 )
                continue

            # Convert the image from BGR to RGB for Qt
            image = cv2.cvtColor( self.image, cv2.COLOR_BGR2RGB )

            # Convert the image into grayscale for face detection
            gray = cv2.cvtColor( image, cv2.COLOR_RGB2GRAY )

            # Detect the faces on the grayscale image
            faces = self.face_cascade.detectMultiScale( gray,
                scaleFactor = 1.1,
                minNeighbors = 5,
                minSize = ( 30, 30 ),
                flags = cv2.cv.CV_HAAR_SCALE_IMAGE )

            # Draw a rectangle for each face on the color image
            for ( x, y, w, h ) in faces :
                cv2.rectangle( image, (x, y), (x+w, y+h), (0, 255, 0), 2 )

            # Send the processed image
            self.image_callback( image )


#
# Qt Widget to detect faces on the images from a USB camera
#
class Camera( vtk.UsbCameraWidget ) :

    #
    # Initialization
    #
    def __init__( self, parent = None ) :

        # Initialize parent class
        super( Camera, self ).__init__( parent )

        # Initialize the image processing thread
        self.face_detection = FaceDetection( self.update_image.emit )
        self.face_detection.start()

    #
    # Process the image from the camera
    #
    def ProcessImage( self, image ) :

        self.face_detection.image = image

    #
    # Close the widget
    #
    def closeEvent( self, event ) :

        # Stop image processing thread
        self.face_detection.running = False
        self.face_detection.join()

        # Close the camera and the widget
        super( Camera, self ).closeEvent( event )


#
# Main application
#
if __name__ == '__main__' :

    application = QtGui.QApplication( sys.argv )
    widget = Camera()
    widget.show()
    sys.exit( application.exec_() )
