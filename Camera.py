#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images from two AVT Manta cameras
#


#
# External dependencies
#
from ctypes import *
from time import sleep


#
# Camera information structure
#
class tPvCameraInfoEx( Structure ) :
    
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


#
# Frame structure
#
class tPvFrame( Structure ) :

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
    
    #
    # Initialization
    #
    def __init__( self, frameSize ) :
		
        self.ImageBuffer = create_string_buffer( frameSize )
        self.ImageBufferSize = c_ulong( frameSize )
        self.AncillaryBuffer = 0
        self.AncillaryBufferSize = 0


#
# Main
#
if __name__ == "__main__" :
	
	
	# Load PvAPI library
	driver = cdll.LoadLibrary( "libPvAPI.so" )
	
	# Initialize the library
	driver.PvInitialize()
	
	# Print version
	pMajor, pMinor = c_int(), c_int()
	driver.PvVersion( byref(pMajor), byref(pMinor) )
	print( 'libPvAPI version {}.{}'.format( pMajor.value, pMinor.value ) )
	
	# Wait for cameras
	print( 'Waiting for cameras...' )
	while not driver.PvCameraCount() :
		sleep( 1 )
	
	# Camera list
	camera_list = ( tPvCameraInfoEx * 20 )()
	camera_number = driver.PvCameraListEx( byref(camera_list), 20, None, sizeof(tPvCameraInfoEx) )
	print( '{} camera found'.format( camera_number ) )
	print( 'Camera list :\n' )
	for i in range( camera_number ) :
		print( 'Camera {} : {}'.format( i, camera_list[i].UniqueID ) )
	
	# Release the library
	driver.PvUnInitialize()
