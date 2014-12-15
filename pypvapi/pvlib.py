"""

Pythonic interface over PvAPI.dll library
PvAPI is supposed to be threadsafe so this library is also suposed to thread safe
Warning: PvAPI.dll uses interrups, this breaks the sleep method!!
this modules provide an alternative sleep method

"""
import time
import os
import numpy as np
from ctypes import POINTER, create_string_buffer, byref, sizeof, Structure, cdll, CFUNCTYPE
from ctypes import c_ulong, c_char, c_int, c_void_p, c_long, c_char_p, c_uint32, c_void_p, c_int64, c_float, c_bool


def sleep(val):
    """
    sleep at minst "val" seconds
    this is independent of interrups
    """
    rest = val
    start = time.time()
    while True:
        time.sleep(rest)
        slept = time.time() - start
        if slept > val:
            return slept
        rest = val - slept

# tPvAccessFlags;
ePvAccessMonitor        = 2 #, // Monitor access: no control, read & listen only
ePvAccessMaster         = 4 #, // Master access: full control
__ePvAccess_force_32    = 0xFFFFFFFF

#typedef enum
class PvAttrFlagClass(object):
    ePvFlagRead         = 0x01 #     // Read access is permitted
    ePvFlagWrite        = 0x02 #     // Write access is permitted
    ePvFlagVolatile     = 0x04 #     // The camera may change the value any time
    ePvFlagConst        = 0x08 #     // Value is read only and never changes


    def __getitem__(self, key):
        st = ""
        if self.ePvFlagRead & key:
            st += "Read "
        if self.ePvFlagWrite & key:
            st += "Write"
        if self.ePvFlagVolatile & key:
            st += "Volatile"
        if self.ePvFlagConst & key:
            st += "Const"
        return st


PvAttrFlags = PvAttrFlagClass()




#tPvInterface
ePvInterfaceFirewire    = 1
ePvInterfaceEthernet    = 2
__ePvInterface_force_32 = 0xFFFFFFFF



class PvDatatypeClass:
    dic = dict( 
        ePvDatatypeUnknown  = 0,
        ePvDatatypeCommand  = 1,
        ePvDatatypeRaw      = 2,
        ePvDatatypeString   = 3,
        ePvDatatypeEnum     = 4,
        ePvDatatypeUint32   = 5,
        ePvDatatypeFloat32  = 6,
        ePvDatatypeInt64    = 7,
        ePvDatatypeBoolean  = 8,
        __ePvDatatypeforce_32 = 0xFFFFFFFF
        )
    rdic = {}

    for k, v in dic.items():
        rdic[v] = k

    def __getitem__(self, key):
        if self.rdic.has_key(key):
            return self.rdic[key]
        elif self.dic.has_key(key):
            return self.dic[key]
        else:
            raise KeyError(key)

    def __getattr__(self, key):
        if self.dic.has_key(key):
            return self.dic[key]
        else:
            raise AttributeError(key)

PvDatatype = PvDatatypeClass()

class PvEventType:
    ePvLinkAdd          = 1 #, // A camera was plugged in
    ePvLinkRemove       = 2 #, // A camera was unplugged
    _ePvLink_reserved1  = 3 #, 
    __ePvLink_force_32  = 0xFFFFFFFF

class PvErrorClass:
    dic = dict( 
        ePvErrSuccess       = 0, #,        // No error
        ePvErrCameraFault   = 1, #,        // Unexpected camera fault
        ePvErrInternalFault = 2, #,        // Unexpected fault in PvApi or driver
        ePvErrBadHandle     = 3, #,        // Camera handle is invalid
        ePvErrBadParameter  = 4, #,        // Bad parameter to API call
        ePvErrBadSequence   = 5, #,        // Sequence of API calls is incorrect
        ePvErrNotFound      = 6, #,        // Camera or attribute not found
        ePvErrAccessDenied  = 7, #,        // Camera cannot be opened in the specified mode
        ePvErrUnplugged     = 8, #,        // Camera was unplugged
        ePvErrInvalidSetup  = 9, #,        // Setup is invalid (an attribute is invalid)
        ePvErrResources     = 10, #,       // System/network resources or memory not available
        ePvErrBandwidth     = 11, #,       // 1394 bandwidth not available
        ePvErrQueueFull     = 12, #,       // Too many frames on queue
        ePvErrBufferTooSmall = 13, #,       // Frame buffer is too small
        ePvErrCancelled     = 14, #,       // Frame cancelled by user
        ePvErrDataLost      = 15, #,       // The data for the frame was lost
        ePvErrDataMissing   = 16, #,       // Some data in the frame is missing
        ePvErrTimeout       = 17, #,       // Timeout during wait
        ePvErrOutOfRange    = 18, #,       // Attr value is out of the expected range
        ePvErrWrongType     = 19, #,       // Attr is not this type (wrong access function) 
        ePvErrForbidden     = 20, #,       // Attr write forbidden at this time
        ePvErrUnavailable   = 21, #,       // Attr is not available at this time
        ePvErrFirewall      = 22, #,       // A firewall is blocking the traffic (Windows only)
        __ePvErr_force_32   = 0xFFFFFFFF
    )
    rdic = {}

    for k, v in dic.items():
        rdic[v] = k

    def __getitem__(self, key):
        if self.rdic.has_key(key):
            return self.rdic[key]
        elif self.dic.has_key(key):
            return self.dic[key]
        else:
            raise KeyError

    def __getattr__(self, key):
        if self.dic.has_key(key):
            return self.dic[key]
        else:
            raise AttributeError


PvError = PvErrorClass()



class tPvCameraInfoEx(Structure):
    _fields_ = [
        ("StructVer", c_ulong),
        ("UniqueId", c_ulong),
        ("CameraName", c_char*32 ),
        ("ModelName", c_char*32 ),
        ("PartNumber", c_char*32), 
        ("SerialNumber", c_char*32), 
        ("FirmwareVersion", c_char*32), 
        ("PermittedAcces", c_ulong),
        ("InterfaceId",c_ulong),
        ("InterfaceType", c_int),
        ]

# Frame image format type
# tPvImageFormat;
class PvFormat:
    ePvFmtMono8         = 0  #,            // Monochrome, 8 bits
    ePvFmtMono16        = 1  #,            // Monochrome, 16 bits, data is LSB aligned
    ePvFmtBayer8        = 2  #,            // Bayer-color, 8 bits
    ePvFmtBayer16       = 3  #,            // Bayer-color, 16 bits, data is LSB aligned
    ePvFmtRgb24         = 4  #,            // RGB, 8 bits x 3
    ePvFmtRgb48         = 5  #,            // RGB, 16 bits x 3, data is LSB aligned
    ePvFmtYuv411        = 6  #,            // YUV 411
    ePvFmtYuv422        = 7  #,            // YUV 422
    ePvFmtYuv444        = 8  #,            // YUV 444
    ePvFmtBgr24         = 9  #,            // BGR, 8 bits x 3
    ePvFmtRgba32        = 10  #,           // RGBA, 8 bits x 4
    ePvFmtBgra32        = 11  #,           // BGRA, 8 bits x 4
    ePvFmtMono12Packed  = 12  #,           // Monochrome, 12 bits, 
    ePvFmtBayer12Packed = 13  #,           // Bayer-color, 12 bits, packed
    __ePvFmt_force_32   = 0xFFFFFFFF



class tPvAttrInfo(Structure):
    _fields_ = [
        ("Datatype", c_int), #// Data type
        ("Flags", c_ulong),           #// Combination of tPvAttr flags
        ("Category", c_char_p),        #// Advanced: see documentation
        ("Impact", c_char_p),          #// Advanced: see documentation
        ("_reserved" , c_ulong*4)    #// Always zero
        ]

    def __str__(self):
        return "Datatype: %s, Flags: %s, Category: %s, Impact: %s" % (PvDatatype[self.Datatype], PvAttrFlags[self.Flags], self.Category, self.Impact)

    def __repr__(self):
        return str(self)


ePvIpConfigPersistent   = 1,           # // Use persistent IP settings
ePvIpConfigDhcp         = 2,           # // Use DHCP, fallback to AutoIP
ePvIpConfigAutoIp       = 4,           # // Use AutoIP only
__ePvIpConfig_force_32  = 0xFFFFFFF

class  tPvIpSettings(Structure):
    _fields_ = [
        #// IP configuration mode: persistent, DHCP & AutoIp, or AutoIp only.
        ("ConfigMode", c_int),
        #// IP configuration mode supported by the camera
        ("ConfigModeSupport", c_ulong),
        #// Current IP configuration.  Ignored for PvCameraIpSettingsChange().  All
        #// values are in network byte order (i.e. big endian).
        ("CurrentIpAddress", c_ulong),
        ("CurrentIpSubnet", c_ulong),
        ("CurrentIpGateway", c_ulong),
        #// Persistent IP configuration.  See "ConfigMode" to enable persistent IP
        #// settings.  All values are in network byte order.
        ("PersistentIpAddr", c_ulong),
        ("PersistentIpSubnet", c_ulong),
        ("PersistentIpGateway", c_ulong),
        ("_reserved1[8]", c_ulong*8)
        ]

class Frame(Structure):
    """Struct that holds the Image data and other relevant information"""
    _fields_ = [
    #input
    ("ImageBuffer", POINTER(c_char)), #void* // image buffer
    ("ImageBufferSize", c_ulong),
    ("AncillaryBuffer", POINTER(c_char)),#void * //buffer to capture associated header and trailer data
    ("AncillaryBufferSize", c_int),
    ("Context", c_void_p*4), #void*[4] // frame-done callback???
    ("_reserved1", c_ulong*8),
    #output
    ("Status", c_int),
    ("ImageSize", c_ulong),
    ("AncillarySize", c_ulong),
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
    
    def __init__(self, size):
        #self.ImageBuffer = (c_char * size)() # this hsould also be correct
        self.ImageBuffer = create_string_buffer(size)
        #self.ImageBuffer = pointer(self.buf)
        self.ImageBufferSize = c_ulong(size)
        self.AncillaryBuffer = create_string_buffer(0)
        self.AncillaryBufferSize = 0

    @property
    def Timestamp(self):
        return (self.TimestampHi << 32) + self.TimestampLo



class tPvIpConfig:
    ePvIpConfigPersistent   = 1#,            // Use persistent IP settings
    ePvIpConfigDhcp         = 2#,            // Use DHCP, fallback to AutoIP
    ePvIpConfigAutoIp       = 4#,            // Use AutoIP only
    __ePvIpConfig_force_32  = 0xFFFFFFFF




class PvException(Exception):
    pass



class PvLib(object):
    """
    Object oriented interface to pvlib module
    """
    def __init__(self, libpvpath=None, verbose=True):
        self.verbose = verbose
        self._initialized = False
        self._cameras = []
        self._dll = None
        if not libpvpath:
            libpvpath = os.path.dirname( __file__)
            if not libpvpath :
                libpvpath = "./"
            self._libpvpath = os.path.join(libpvpath , "libPvAPI.so")
        else:
            self._libpvpath = libpvpath 


        self._initialize()

    def cleanup(self):
        for cam in self._cameras:
            cam.close()
        if self._initialized:
            self._unInitialize()
            self._initialized = False

    def __del__(self):
        self.cleanup()

    def _log(self, *args):
        s = ""
        for i in args:
            s += " " + str(i)
        if self.verbose:
            print "pvlib: ", s 


    def _initialize(self):
        self._log( "Loading PvApi: ", self._libpvpath)
        self._dll = cdll.LoadLibrary(self._libpvpath)
        ret = self._dll.PvInitialize()
        if ret != 0:
            raise PvException("initialization failed", ret)
        self._log( "waiting for initalization")
        sleep(1)
        self._log("initalized")
        self._initialized = True


    def getCameras(self):
        """
        return a list of all cameras found by PvApi
        """
        count = self._dll.PvCameraCount()
        caminfos = tPvCameraInfoEx * count 
        caminfos = caminfos()
        newcount = c_long()
        nb = self._dll.PvCameraListEx(byref(caminfos), count,  byref(newcount), sizeof(tPvCameraInfoEx))
        if nb < count: # do not return None objects
            cams = cams[0:nb]
        newinfos = []
        # first remove from list cameras which allready have a camera object created
        #print "initial ", [ i.UniqueId for i in caminfos]
        currentcams = []
        for info in caminfos:
            add = True
            for cam in self._cameras:
                if cam.id == info.UniqueId: # that camera object is allready created
                    #print "Camera ", cam.id, " allready exists"
                    add = False
                    currentcams.append(cam)
            if add:
                newinfos.append(info)
        newcams = [Camera(self._dll, info) for info in newinfos] 

        self._cameras = currentcams + newcams 
        return  self._cameras 

    def _unInitialize(self):
        self._log("UnInitializing libPv")
        if self._dll:
            self._dll.PvUnInitialize()


    #start test functions
    def _registerLinkAdd(self):
        CMPFUNC = CFUNCTYPE(c_void_p, POINTER(c_int), c_int, c_int, c_ulong) 
        func = CMPFUNC(_newCam)
        self._dll.PvLinkCallbackRegister(func, PvEventType.ePvLinkAdd, 1)

    def _newCam(self, a, b, c):
        print "new cam!!", a, b, c

    def _registerLinkRemove(self, func):
        self._dll.PvLinkCallbackRegister(func, PvEventType.ePvLinkRemove, 0)

    def _unRegisterCallback(self, func):
        self._dll.PvLinkCallbackUnRegister(func, PvEventType.ePvLinkRemove)
        self._dll.PvLinkCallbackUnRegister(func, PvEventType.ePvLinkAdd)


    #end test functions


class Camera(object):
    """
    Camera objects are usually constructed by calling getCameras() after initialize()
    The Camera class take a camera info object or an ip address as argument
    """
    def __init__(self, dll, arg, verbose=True):
        self._dll = dll
        self._arg = arg
        self.verbose = verbose
        self.attributes = []
        self.info = None
        self.name = "Unknown" 
        self.model = "Unknown"
        self.id = 0 
        self.ip = ""
        self.serialNumber = "" 
        self.opened = False
        self.frameSize = 0 
        self._handle = c_void_p()
        self._timestampFrequency = None
        try:
            self.open()
        except PvException, ex:
            print "Opening of camera %s failed: " % self.name, ex


    def open(self):
        arg = self._arg
        if type(arg) == tPvCameraInfoEx:
            #we got caminfo as arg
            self._setMyAttr(arg)
            self.getHandleById(arg.UniqueId)
            self.opened = True
            self.serialNumber = arg.SerialNumber
            self.ip = self.getIpAddress()
        elif type(arg) == str:
            self._log("Opening Camera using IP address: ", arg)
            #FIXME: it seems broken
            #suppose we got IP address"
            self.getHandleByIP(arg)
            self.name = self.getAttr("CameraName")
            self.model = self.getAttr("ModelName")
            self.id = self.getAttr("UniqueId")
            self.serialNumber = self.getAttr("SerialNumber")
        else:
            raise PvException("Bad argument to Camera Constructor")

        self.frameSize = self.getUint32Attr("TotalBytesPerFrame")
        self.attributes = self.getAttrNames()
        #self.width = self.getUint32Attr("Width")
        #print "Image width is ", self.width
        #self.height = self.getUint32Attr("Height")
        #print "Image height is ", self.height

    def _setMyAttr(self, info):
        self.info = info
        self.name = str(info.CameraName)
        self.model = str(info.ModelName)
        self.id = int(info.UniqueId)

    def getHandleByIP(self, ip):
        err = self._dll.PvCameraOpenByAddr(ip, ePvAccessMaster, byref(self._handle))
        if err != 0:
            raise PvException( "Got Error message when opening camera: ", err, PvError[err], ip, self._handle, self._handle.value)

    def getHandleById(self, Id):
        err = self._dll.PvCameraOpen(Id, ePvAccessMaster, byref(self._handle))
        if err != 0:
            #opening failed , try to close then re-opening it
            err = self._dll.PvCameraClose( self._handle)
            err = self._dll.PvCameraOpen(Id, ePvAccessMaster, byref(self._handle))
            if err != 0:
                raise PvException( "Got Error message when opening camera: ", err, PvError[err], Id, self._handle, self._handle.value)
 

    def getAttrNames(self):
        """
        Ask the camera for the list of its attributes
        """
        pListAttr = POINTER(c_char_p)()
        pLength = c_long()
        err  = self._dll.PvAttrList(self._handle, byref(pListAttr), byref(pLength))
        if err != 0:
            raise PvException( "Got Error message when querying camera: ", err, PvError[err], self._handle, self._handle.value)
        return [pListAttr[i] for i in range(0, pLength.value)]

        #return [pListAttr[i] for i in range(0, pLength.value)]
 
    def runCommand(self, cmd):
        return self._dll.PvCommandRun(self._handle, cmd)

    def getAttrInfo(self, name):
        info = tPvAttrInfo()
        self._dll.PvAttrInfo(self._handle, name, byref(info))
        return info

    def getAttr(self, name):
        """
        get value of an attribute given its name
        """
        info = self.getAttrInfo(name)
        dtype = info.Datatype
        if dtype == PvDatatype.ePvDatatypeEnum: 
            return self.getEnumAttr(name)
        elif dtype == PvDatatype.ePvDatatypeUint32:
            return self.getUint32Attr(name)
        elif dtype == PvDatatype.ePvDatatypeFloat32:
            return self.getFloat32Attr(name)
        elif dtype == PvDatatype.ePvDatatypeInt64:
            return self.getInt64Attr(name)
        elif dtype == PvDatatype.ePvDatatypeBoolean:
            return self.getBooleanAttr(name)
        else:
            raise PvException("Attr type not implemented yet for type; ", dtype)

    def setAttr(self, name, val):
        """
        set value of an attribute 
        """
        info = self.getAttrInfo(name)
        dtype = info.Datatype
        print dtype, PvDatatype.ePvDatatypeEnum
        if dtype == PvDatatype.ePvDatatypeEnum: 
            return self.setEnumAttr(name, val)
        elif dtype == PvDatatype.ePvDatatypeUint32:
            return self.setUint32Attr(name, val)
        elif dtype == PvDatatype.ePvDatatypeFloat32:
            return self.setFloat32Attr(name, val)
        elif dtype == PvDatatype.ePvDatatypeInt64:
            return self.setInt64Attr(name, val)
        elif dtype == PvDatatype.ePvDatatypeBoolean:
            return self.setBooleanAttr(name, val)
        else:
            raise PvException("Attr type not implemented yet for type; ", dtype)


       
    def getIpSettings(self):
        ipinfo = tPvIpSettings()
        self._dll.PvCameraIpSettingsGet(self.id, byref(ipinfo))
        return ipinfo

    def getIpAddress(self):
        info = self.getIpSettings()
        l = info.CurrentIpAddress
        ip = (l & 0xff, l >> 8 & 0xff, l >> 16 & 0xff, l >> 24 & 0xff)
        ip = map(str, ip)
        return ip[0] +"." + ip[1] + "." + ip[2] + "." + ip[3]  

    def getSingleFrame(self):
        """
        deprecated
        """
        self.startCaptureTrigger()
        frame = self.capture()
        self.stopCapture()
        return frame

    def getSingleNumpyArray(self):
        """
        deprecated
        """
        self.startCaptureTrigger()
        np_image = self.getNumpyArray()
        self.stopCapture()
        return np_image
    
    def getFrame(self):
        """
        return a frame from the camera, make sure to call startCapture before
        """
        return self.capture()
    
    def getNumpyArray(self):
        """
        return a frame from the camera as a numoy array, make sure to call startCapture before
        """
        for i in range(0, 15): #usually the first frame is ok, but shit happens regularily
            frame = self.capture()
            if frame.ImageSize == self.frameSize:
                im = np.array([ord(frame.ImageBuffer[x]) for x in range(frame.ImageSize)], dtype=np.uint8)
                #im = np.fromiter((ord(frame.ImageBuffer[x]) for x in range(frame.ImageSize)), dtype=np.uint8)
                im.shape = (frame.Height, frame.Width)
                return im
            self._log("Got a bad frame from camera ", self.name, self.id)
        raise PvException

    def startCaptureStream(self):
        """
        Start streaming pictures as fast as possible from camera to pvapi
        """
        #fra Johannes, I do not know why, probably unncessary
        #v = self.getUint32Attr("PacketSize")
        #self._dll.PvCaptureAdjustPacketSize(self._handle, v)
        # end johannes
        self.setEnumAttr("AcquisitionMode", "Continuous") 
        self.setEnumAttr("FrameStartTriggerMode","Freerun")
        self._dll.PvCaptureStart(self._handle) 
        self.runCommand("AcquisitionStart")

    def startCapture(self):
        """
        set the camera in capture mode
        """
        self.startCaptureTrigger()

    def startCaptureTrigger(self):
        """
        set the camera in capture mode
        """
        self.setEnumAttr("AcquisitionMode", "Continuous") 
        self.setEnumAttr("FrameStartTriggerMode","Software")
        self._dll.PvCaptureStart(self._handle) 
        self.runCommand("AcquisitionStart")
        #print self.runCommand("FrameStartTriggerSoftware")
        #return frame 

    def stopCapture(self):
        self.runCommand("AcquisitionStop")
        self._dll.PvCaptureEnd(self._handle) 

    def captureState(self):
        """
        Return the current capture state
        """
        l = c_ulong()
        err = self._dll.PvCaptureQuery(self._handle, byref(l))
        if err != 0:
            raise PvException(err, PvError[err])
        return l.value

    def capture(self):
        """
        return a frame from the camera
        """
        frame = Frame(self.frameSize)
        err = self._dll.PvCaptureQueueFrame(self._handle, byref(frame), None)
        if err != 0:
            raise PvException("Capturing image raised error nr: ", err, PvError[err])
        self.runCommand("FrameStartTriggerSoftware")#this is useless in stream mode
        err = self._dll.PvCaptureWaitForFrameDone(self._handle, byref(frame), 5000)
        if err != 0:
            raise PvException("waiting for image buffer raised error nr: ", err, PvError[err])
        return frame

    def getUint32Attr(self, name):
        att = c_uint32()
        err = self._dll.PvAttrUint32Get(self._handle, name, byref(att))
        if err:
            raise PvException("Error getting attribute value:", err, PvError[err])
        return att.value

    def getFloat32Attr(self, name):
        att = c_float() #this might be platform specific
        err = self._dll.PvAttrFloat32Get(self._handle, name, byref(att))
        if err:
            raise PvException("Error getting attribute value:", err, PvError[err])
        return att.value

    def getInt64Attr(self, name):
        att = c_int64() #this might be platform specific
        err = self._dll.PvAttrInt64Get(self._handle, name, byref(att))
        if err:
            raise PvException("Error getting attribute value:", err, PvError[err])
        return att.value

    def getBooleanAttr(self, name):
        att = c_bool() #this might be platform specific
        err = self._dll.PvAttrBooleanGet(self._handle, name, byref(att))
        if err:
            raise PvException("Error getting attribute value:", err, PvError[err])
        return att.value

    def setUint32Attr(self, name, val):
        err = self._dll.PvAttrUint32Set(self._handle, name, val)
        if err:
            raise PvException("Error setting attribute %s the value %s: %s %s" % ( err, PvError[err], name, val))
        return err

    def setFloat32Attr(self, name, val):
        err = self._dll.PvAttrFloat32Set(self._handle, name, val)
        if err:
            raise PvException("Error setting attribute %s the value %s: %s %s" % ( err, PvError[err], name, val))
        return err

    def setInt64Attr(self, name, val):
        err = self._dll.PvAttrInt64Set(self._handle, name, val)
        if err:
            raise PvException("Error setting attribute %s the value %s: %s %s" % ( err, PvError[err], name, val))
        return err

    def setBooleanAttr(self, name, val):
        err = self._dll.PvAttrBooleanSet(self._handle, name, val)
        if err:
            raise PvException("Error setting attribute %s the value %s: %s %s" % ( err, PvError[err], name, val))
        return err

    def setExposure(self, val):
        self.setEnumAttr("ExposureMode", "Manual")
        self.setUint32Attr("ExposureValue", val)

    def getEnumAttr(self, name):
        val = c_char * 255
        val = val()
        psize = c_long()
        self._dll.PvAttrEnumGet(self._handle, name, byref(val), 255, byref(psize))
        return val[:psize.value]


    def setEnumAttr(self, name, val):
        return self._dll.PvAttrEnumSet(self._handle, name, val)


    def getFrameTimestamp(self, frame):
        """
        helper method to return a frame timestamp in second
        """
        if not self._timestampFrequency:
            self._timestampFrequency = self.getAttr("TimeStampFrequency")
        return float(frame.Timestamp)  / self._timestampFrequency




    def close(self):
        self._log("Cleanup Camera: ", self)
        self._dll.PvCameraClose(self._handle)
    
    def __str__(self):
        return "Camera[name=%s, id=%s, model=%s, dev=%s, ip=%s]" % (self.name, self.id, self.model, self.serialNumber, self.ip)

    def __repr__(self):
        return self.__str__()

    def _log(self, *args):
        s = ""
        for i in args:
            s += " " + str(i)
        if self.verbose:
            print "pvlib: ", s 


if __name__ == "__main__":
    #dll = cdll.LoadLibrary("./libPvAPI.so")
    #ret = dll.PvInitialize()
    #if ret != 0:
        #print "initialization failed"
    #caminfo = tPvCameraInfo()
    #count = dll.PvCameraList(byref(caminfo), 1, None)
    #print count
    #print caminfo
    #dll.PvUnInitialize()
    print "\n!!!Starting test program for libpv!!!\n"
    pv = PvLib(verbose=True)
    cams = pv.getCameras()
    print "Camera List: ", cams
    if cams:
        cam = cams[0] 
        if cam.opened:
            cam.startCaptureTrigger()
            frame = cam.capture()
            cam.stopCapture()
            from IPython.frontend.terminal.embed import InteractiveShellEmbed
            ipshell = InteractiveShellEmbed()
            ipshell(local_ns=locals())
        else:
            print "Camera is not opened"
    else:
        print "No camera found on network"



