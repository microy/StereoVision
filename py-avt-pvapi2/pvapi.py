# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 15:17:31 2011

True Camera API that binds to the underlying PvAPI SDK.
This is the result of a lot of blood, sweat, and pain.

Not all functions are implemented, but example in example.py 
demonstrates successful initialization of the camera, captures a frame,
and then shuts down the driver engine.

multicamera.py shows how multiple cameras can be opened and displayed simultaneously.

Updated in July-September 2011 by Mikael Mannberg, Cranfield University, United Kingdom:
- Added error codes
- Added further configuration functions
- Support for Windows, Linux and Mac OS X on 32 and 64bit architectures
- Added Camera class to simplify camera management and multi-camera use

@author: coryli, mikaelmannberg
"""


from ctypes import *
import platform, sys
import numpy

class ResultValues():
    ePvErrSuccess       = 0        # No error
    ePvErrCameraFault   = 1        # Unexpected camera fault
    ePvErrInternalFault = 2        # Unexpected fault in PvAPI or driver
    ePvErrBadHandle     = 3        # Camera handle is invalid
    ePvErrBadParameter  = 4        # Bad parameter to API call
    ePvErrBadSequence   = 5        # Sequence of API calls is incorrect
    ePvErrNotFound      = 6        # Camera or attribute not found
    ePvErrAccessDenied  = 7        # Camera cannot be opened in the specified mode
    ePvErrUnplugged     = 8        # Camera was unplugged
    ePvErrInvalidSetup  = 9        # Setup is invalid (an attribute is invalid)
    ePvErrResources     = 10       # System/network resources or memory not available
    ePvErrBandwidth     = 11       # 1394 bandwidth not available
    ePvErrQueueFull     = 12       # Too many frames on queue
    ePvErrBufferTooSmall= 13       # Frame buffer is too small
    ePvErrCancelled     = 14       # Frame cancelled by user
    ePvErrDataLost      = 15       # The data for the frame was lost
    ePvErrDataMissing   = 16       # Some data in the frame is missing
    ePvErrTimeout       = 17       # Timeout during wait
    ePvErrOutOfRange    = 18       # Attribute value is out of the expected range
    ePvErrWrongType     = 19       # Attribute is not this type (wrong access function) 
    ePvErrForbidden     = 20       # Attribute write forbidden at this time
    ePvErrUnavailable   = 21       # Attribute is not available at this time
    ePvErrFirewall      = 22       # A firewall is blocking the traffic (Windows only)
    
    errors =   ['ePvErrSuccess', 'ePvErrCameraFault', 'ePvErrInternalFault', 'ePvErrBadHandle', \
        'ePvErrBadParameter', 'ePvErrBadSequence', 'ePvErrNotFound', 'ePvErrAccessDenied', \
        'ePvErrUnplugged', 'ePvErrInvalidSetup', 'ePvErrResources', 'ePvErrBandwidth', \
        'ePvErrQueueFull', 'ePvErrBufferTooSmall', 'ePvErrCancelled', 'ePvErrDataLost', \
        'ePvErrDataMissing', 'ePvErrTimeout', 'ePvErrOutOfRange', 'ePvErrWrongType',\
        'ePvErrForbidden', 'ePvErrUnavailable', 'ePvErrFirewall']
    
    descriptions = ['No error', 'Unexpected camera fault','Unexpected fault in PvAPI or driver','Camera handle is invalid',\
            'Bad parameter to API call', 'Sequence of API calls is incorrect', 'Camera or attribute not found',\
            'Camera cannot be opened in the specified mode', 'Camera was unplugged', 'Setup is invalid (an attribute is invalid)',\
            'System/network resources or memory not available', '1394 bandwidth not available', 'Too many frames on queue',\
            'Frame buffer is too small', 'Frame cancelled by user', 'The data for the frame was lost', 'Some data in the frame is missing',\
            'Timeout during wait', 'Attribute value is out of the expected range', 'Attribute is not this type (wrong access function)',\
            'Attribute write forbidden at this time', 'Attribute is not available at this time', 'A firewall is blocking the traffic (Windows only)']

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
    
    def __init__(self, frameSize):
        self.ImageBuffer = create_string_buffer(frameSize)
        self.ImageBufferSize = c_ulong(frameSize)
        self.AncillaryBuffer = 0
        self.AncillaryBufferSize = 0

e = ResultValues()

class Camera:
	
    dll				= None
    apiData 		= None
    handle			= None
    is64bit         = False

    width, height, channels = 0, 0, 1
    dtype           = 8
    frame 			= None
    pixelFormat		= None

    name            = None
    uid             = None
	
    def __init__(self, driver, apiData):
        self.dll     = driver.dll
        self.apiData = apiData
        self.is64bit = sys.maxsize>2**32
		
        self.name = apiData.CameraName
        self.uid  = apiData.UniqueId
		
        self.handle = self.open(apiData.UniqueId)

        self.width  = self.attrUint32Get('Width')
        self.height = self.attrUint32Get('Height')
        
        # Set the Acquisition Mode. This is SingleFrame to ensure that we 
        # have control over the camera and know exactly when the frame was captured
        result = self.attrEnumSet('AcquisitionMode','SingleFrame')
        if result != e.ePvErrSuccess:
            self.handleError(result)  

        # Set the correct number of channels and the data type
        # and allocate a frame of the correct size.
        self.handlePixelFormat()

        # Start capture
        self.captureStart()

    def open(self,uniqueId):
        """Opens a particular camera. Returns the camera's handle"""
        if self.is64bit:
            cameraHandle = c_uint64()
        else:
            cameraHandle = c_uint()
        self.dll.PvCameraOpen(uniqueId,0,byref(cameraHandle))
        return cameraHandle

    def close(self):
        """Closes a camera given a handle"""
        if self.captureQuery(): self.captureEnd()
        result = self.dll.PvCameraClose(self.handle)
        return result

    def captureStart(self):
        """Begins Camera Capture"""
        return self.dll.PvCaptureStart(self.handle)

    def captureEnd(self):
        """Ends Camera Capture"""
        return self.dll.PvCaptureEnd(self.handle)

    def captureQuery(self):
        """Checks if the camera is running"""
        isRunning = c_ulong()
        self.dll.PvCaptureQuery(self.handle, byref(isRunning))
        return isRunning

    def capture(self):
        """ Convenience function that automatically queues a frame, initiates capture
            and converts the completed frame into a Numpy array for easy integration with
            OpenCV and other libraries """

        # Queue the frame
        self.dll.PvCaptureQueueFrame(self.handle,byref(self.frame),None)

        # Start acquisition
        result = self.commandRun('AcquisitionStart')
        if result != e.ePvErrSuccess:
            self.handleError(result)  

        # Wait for the frame to complete
        self.dll.PvCaptureWaitForFrameDone(self.handle,byref(self.frame),60000)

        # Return a numpy array
        return self.frameToArray()

    def createFrame(self, frameSize = 0):
        """ Creates a frame with a given size """
        if frameSize == 0:
            frameSize = self.attrUint32Get('TotalBytesPerFrame')
        return Frame(frameSize)

    def waitForFrameDone(self):
        result = self.dll.PvCaptureWaitForFrameDone(self.handle,byref(self.frame),1000)
        return result

    def frameToArray(self):
        """ Converts a Frame buffer to a Numpy array """
        # TODO: ADD SUPPORT FOR MULTIPLE CHANNELS
        if self.dtype == 8:
            image = numpy.fromstring(self.frame.ImageBuffer[0:(self.frame.ImageBufferSize)], dtype=numpy.uint8)
        if self.dtype == 16:
            image = numpy.fromstring(self.frame.ImageBuffer[0:(self.frame.ImageBufferSize)], dtype=numpy.uint16)
        image = image.reshape(self.height, self.width, self.channels)
        return image

    def attrEnumSet(self,param,value):
        """Set a particular enum attribute given a param and value"""
        result = self.dll.PvAttrEnumSet(self.handle,param,value)
        if (result == 0) and (param == 'PixelFormat'): self.handlePixelFormat()
        return result

    def attrEnumGet(self,param):
        """Reads a particular enum attribute given a param"""
        val = create_string_buffer(20)
        result = self.dll.PvAttrEnumGet(self.handle,param, byref(val), len(val), None)
        return val.value

    def commandRun(self,command):
        """Runs a particular command valid in the Camera and Drive Attributes"""
        return self.dll.PvCommandRun(self.handle,command)

    def attrUint32Get(self,name):
        """Returns a particular integer attribute"""
        val = c_uint()
        self.dll.PvAttrUint32Get(self.handle,name,byref(val))
        return val.value

    def attrUint32Set(self, param, value):
        """Sets a particular integer attribute"""
        val = c_uint32(value)
        result = self.dll.PvAttrUint32Set(self.handle,param,val)
        return result

    def adjustPacketSize(self, value):
        """ Sets the Packet Size for the camera. Should match your network card's MTU """
        val = c_uint(value)
        result = self.dll.PvCaptureAdjustPacketSize(self.handle,byref(val))
        return result    

    def handlePixelFormat(self):
        """ Configures the camera class and allocates the correct Frame 
            Run this every time the PixelFormat is changed """

        self.pixelFormat = self.attrEnumGet('PixelFormat')

        if self.pixelFormat == 'Mono8':
           self.channels = 1
           self.dtype = 8
        if self.pixelFormat == 'Mono16':
           self.channels = 1
           self.dtype = 16
        if self.pixelFormat == 'Bayer8':
           self.channels = 1
           self.dtype = 8
        if self.pixelFormat == 'Bayer16':
           self.channels = 1
           self.dtype = 16
        if self.pixelFormat == 'Rgb24':
           raise NotImplementedError('The requested color mode is not yet supported. Change the color mode using the SampleViewer and try again.')
        if self.pixelFormat == 'Rgb48':
           raise NotImplementedError('The requested color mode is not yet supported. Change the color mode using the SampleViewer and try again.')
        if self.pixelFormat == 'Yuv411':
           raise NotImplementedError('The requested color mode is not yet supported. Change the color mode using the SampleViewer and try again.')
        if self.pixelFormat == 'Yuv422':
           raise NotImplementedError('The requested color mode is not yet supported. Change the color mode using the SampleViewer and try again.')
        if self.pixelFormat == 'Yuv444':
           raise NotImplementedError('The requested color mode is not yet supported. Change the color mode using the SampleViewer and try again.')

        # Allocate a frame with the correct size
        self.frame = self.createFrame()

    def handleError(self, result):
        print e.descriptions[result] + ' ('+ e.errors[result] + ')'
        raise
        exit()
		

class PvAPI:
    """Handles the driver"""

    def __init__(self):
    
        # Load the correct version of the driver
        path = "PvAPI/" + platform.system() + "/"

        is64bit = sys.maxsize>2**32
        if is64bit:
            path = path + "x64/"
        else:
            path = path + "x86/"

        if platform.system() == "Linux":  path = path + "libPvAPI.so"
        if platform.system() == "Darwin": path = path + "libPvAPI.dylib"
        if platform.system() == "Windows": path = path + "PvAPI.dll"        
        
        if platform.system() == "Windows":
            self.dll = windll.LoadLibrary(path)            
        else:
            self.dll = cdll.LoadLibrary(path)

        self.initialize()

    def __del__(self):
        self.uninitialize()

    def version(self):
        """Returns a tuple of the driver version"""
        pMajor = c_int()
        pMinor = c_int()
        self.dll.PvVersion(byref(pMajor),byref(pMinor))
        return (pMajor.value,pMinor.value)
        
    def initialize(self):
        """Initializes the driver.  Call this first before anything"""
        result = self.dll.PvInitialize()
        return result
    
    def cameraCount(self):
        """Returns the number of attached cameras"""
        return self.dll.PvCameraCount()

    def uninitialize(self):
        """Uninitializes the camera interface"""
        result = self.dll.PvUnInitialize()
        return result

    def cameraList(self):
        """Returns a list of all attached cameras as CameraInfoEx"""
        var = (CameraInfoEx*20)()
        self.dll.PvCameraListEx(byref(var), 20, None, sizeof(CameraInfoEx))
        return var
        


