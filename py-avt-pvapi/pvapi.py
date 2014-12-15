# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 15:17:31 2011

True Camera API that binds to the underlying DLL PvAPI.dll
This is the result of a lot of blood, sweat, and pain.

Not all functions are implemented, but example in example.py 
demonstrates successful initialization of the camera, captures a frame,
and then shuts down the driver engine.

@author: coryli
"""


from ctypes import *
import logging
from time import sleep

import numpy
from matplotlib import pylab


class CameraInfoEx(Structure):
    """Struct that holds information about the camera"""
    
    _fields_ = [
    ("StructVer",c_ulong),
    ("UniqueId", c_ulong),
    ("CameraName", c_char*32),
    ("ModelName", c_char*32),
    ("PartNumber", c_char*32),
    ("SerialNumber", c_char*32),
    ("FirmwareVersion", c_char*32),
    ("PermittedAccess", c_long),
    ("InterfaceId",c_ulong),
    ("InterfaceType",c_int)
    ]

class Frame(Structure):
    """Struct that holds the frame and other relevant information"""

    
    _fields_ = [
    ("ImageBuffer",POINTER(c_char)),
    ("ImageBufferSize",c_ulong),
    ("AncillaryBuffer",c_int),
    ("AncillaryBufferSize",c_int),
    ("Context",c_int*4),
    ("_reserved1",c_ulong*8),

    ("Status",c_int),
    ("ImageSize",c_ulong),
    ("AncillarySize",c_ulong),
    ("Width",c_ulong),
    ("Height",c_ulong),
    ("RegionX",c_ulong),
    ("RegionY",c_ulong),
    ("Format",c_int),
    ("BitDepth",c_ulong),
    ("BayerPattern",c_int),
    ("FrameCount",c_ulong),
    ("TimestampLo",c_ulong),
    ("TimestampHi",c_ulong),
    ("_reserved2",c_ulong*32)    
    ]
    
    def __init__(self):
        self.ImageBuffer = create_string_buffer(322752)
        self.ImageBufferSize = c_ulong(322752)
        self.AncillaryBuffer = 0
        self.AncillaryBufferSize = 0




class CameraDriver:
    """The main class that drives the camera"""

    def __init__(self):
        self.dll = windll.LoadLibrary("PvAPI.dll")

    def version(self):
        """Returns a tuple of the driver version"""
        pMajor = c_int()
        pMinor = c_int()
        self.dll.PvVersion(byref(pMajor),byref(pMinor))
        return (pMajor.value,pMinor.value)
        
    def initialize(self):
        """Initializes the camera.  Call this first before anything"""
        logging.info("Driver Loaded")
        result = self.dll.PvInitialize()
        sleep(1)
        return result
    
    def cameraCount(self):
        """Returns the number of attached cameras"""
        return self.dll.PvCameraCount()

    def uninitialize(self):
        """Uninitializes the camera interface"""
        logging.info("Driver Unloaded")
        result = self.dll.PvUnInitialize()
        return result
    
    def cameraOpen(self,uniqueId):
        """Opens a particular camera. Returns the camera's handle"""
        logging.info("Opening Camera")
        camera = c_uint()
        self.dll.PvCameraOpen(uniqueId,0,byref(camera))
        return camera
    
    def cameraClose(self,camera):
        """Closes a camera given a handle"""
        logging.info("Closing Camera")
        self.dll.PvCameraClose(camera)


    def cameraList(self):
        """Returns a list of all attached cameras as CameraInfoEx"""
        var = (CameraInfoEx*10)()
        self.dll.PvCameraListEx(byref(var), 1, None, sizeof(CameraInfoEx))
        return var
        
    def captureStart(self,handle):
        """Begins Camera Capture"""
        return self.dll.PvCaptureStart(handle)
    
    def captureEnd(self,handle):
        """Ends Camera Capture"""
        return self.dll.PvCaptureEnd(handle)
        
    def captureFrame(self,handle):
        """Function that loads up a frame buffer,
        then waits for said frame buffer to be filled"""
        frame = Frame()
        self.dll.PvCaptureQueueFrame(handle,byref(frame),None)
        self.dll.PvCaptureWaitForFrameDone(handle,byref(frame),60000)
        return frame
    
    def attrEnumSet(self,handle,param,value):
        """Set a particular enum attribute given a param and value"""
        return self.dll.PvAttrEnumSet(handle,param,value)
        
    def commandRun(self,handle,command):
        """Runs a particular command valid in the Camer and Drive Attributes"""
        return self.dll.PvCommandRun(handle,command)
        
    def attrUint32Get(self,handle,name):
        """Returns a particular integer attribute"""
        val = c_uint()
        self.dll.PvAttrUint32Get(handle,name,byref(val))
        return val.value
		
		


