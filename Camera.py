#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images from two AVT Manta cameras
#


#
# External dependencies
#
import ctypes
import time
import cmd
import socket


#
# Camera information structure
#
class tPvCameraInfoEx( ctypes.Structure ) :
    
    _fields_ = [
    ("StructVer", ctypes.c_ulong),
    ("UniqueId", ctypes.c_ulong),
    ("CameraName", ctypes.c_char*32),
    ("ModelName", ctypes.c_char*32),
    ("PartNumber", ctypes.c_char*32),
    ("SerialNumber", ctypes.c_char*32),
    ("FirmwareVersion", ctypes.c_char*32),
    ("PermittedAccess", ctypes.c_long),
    ("InterfaceId", ctypes.c_ulong),
    ("InterfaceType", ctypes.c_int)
    ]


#
# Frame structure
#
class tPvFrame( ctypes.Structure ) :

    _fields_ = [
    ("ImageBuffer", ctypes.POINTER(ctypes.c_char)),
    ("ImageBufferSize", ctypes.c_ulong),
    ("AncillaryBuffer", ctypes.c_int),
    ("AncillaryBufferSize", ctypes.c_int),
    ("Context", ctypes.c_int*4),
    ("_reserved1", ctypes.c_ulong*8),
    ("Status", ctypes.c_int),
    ("ImageSize", ctypes.c_ulong),
    ("AncillarySize", ctypes.c_ulong),
    ("Width", ctypes.c_ulong),
    ("Height", ctypes.c_ulong),
    ("RegionX", ctypes.c_ulong),
    ("RegionY", ctypes.c_ulong),
    ("Format", ctypes.c_int),
    ("BitDepth", ctypes.c_ulong),
    ("BayerPattern", ctypes.c_int),
    ("FrameCount", ctypes.c_ulong),
    ("TimestampLo", ctypes.c_ulong),
    ("TimestampHi", ctypes.c_ulong),
    ("_reserved2", ctypes.c_ulong*32)    
    ]
    
    #
    # Initialization
    #
    def __init__( self, frameSize ) :
		
        self.ImageBuffer = ctypes.create_string_buffer( frameSize )
        self.ImageBufferSize = ctypes.c_ulong( frameSize )
        self.AncillaryBuffer = 0
        self.AncillaryBufferSize = 0


#
# Shell to interface the PvAPI library
#
class Shell( cmd.Cmd ) :
	
	
	#
	# Shell customization
	#
	prompt = '> '
	intro = '\n~~ AVT PvAPI SDK Interface ~~\n'
	ruler = '-'


	#
	# Pre main loop event
	#
	def preloop( self ) :
		
		# Load PvAPI library
		self.driver = ctypes.cdll.LoadLibrary( 'libPvAPI.so' )
		
		# Initialize the library
		if self.driver.PvInitialize() :
			print( 'libPvAPI initialisation failed.' )
		
	
	#
	# Post main loop event
	#
	def postloop( self ) :

		# Release the library
		self.driver.PvUnInitialize()


	#
	# Print livPvAPI version number
	#
	def do_version( self, line ) :
		
		pMajor, pMinor = ctypes.c_int(), ctypes.c_int()
		self.driver.PvVersion( ctypes.byref(pMajor), ctypes.byref(pMinor) )
		print( 'libPvAPI version {}.{}'.format( pMajor.value, pMinor.value ) )
	
	
	#
	# List available cameras
	#
	def do_cameralist( self, line ) :
		
		self.camera_list = ( tPvCameraInfoEx * 20 )()
		self.camera_number = self.driver.PvCameraListEx( ctypes.byref(self.camera_list), 20, None, ctypes.sizeof(tPvCameraInfoEx) )
		print( '{} camera found'.format( self.camera_number ) )
		print( 'Camera list :\n' )
		for i in range( self.camera_number ) :
			print( 'Camera {} : {} {} {}'.format( i, self.camera_list[i].CameraName, self.camera_list[i].ModelName, self.camera_list[i].UniqueID ) )


	#
	# Connect a camera via its ID
	#
	def do_connect( self, camera_id ) :
		
		self.camera_handle = ctypes.c_void_p()
		if self.driver.PvCameraOpen( camera_id, 0, ctypes.byref(self.camera_handle) ) :
			print( 'Camera connection failed' )


	#
	# Connect a camera via its IP address
	#
	def do_ipconnect( self, ip_address ) :
		
		self.camera_handle = ctypes.c_void_p()
		if self.driver.PvCameraOpenByAddr( socket.inet_aton(ip_address), 0, ctypes.byref(self.camera_handle) ) :
			print( 'Camera connection failed' )

	#
	# Disconnect the camera
	#
	def do_disconnect( self, line ) :
		
		if self.driver.PvCameraClose( self.camera_handle ) :
			print( 'Camera disconnection failed' )


		
	#
	# Quit gracefully with Ctrl + D
	#
	def do_EOF( self, line ) :
		
		return True
	
	
	#
	# Handle empty lines
	#
	def emptyline( self ) :
		
         pass


#
# Main
#
if __name__ == "__main__" :
	
	Shell().cmdloop()

	
	
	
	#~ # Load PvAPI library
	#~ driver = ctypes.cdll.LoadLibrary( "libPvAPI.so" )
	#~ 
	#~ # Initialize the library
	#~ driver.PvInitialize()
	#~ 
	#~ # Print version
	#~ pMajor, pMinor = ctypes.c_int(), ctypes.c_int()
	#~ driver.PvVersion( ctypes.byref(pMajor), ctypes.byref(pMinor) )
	#~ print( 'libPvAPI version {}.{}'.format( pMajor.value, pMinor.value ) )
	#~ 
	#~ # Wait for cameras
	#~ print( 'Waiting for cameras...' )
	#~ while not driver.PvCameraCount() :
		#~ time.sleep( 1 )
	#~ 
	#~ # Camera list
	#~ camera_list = ( tPvCameraInfoEx * 20 )()
	#~ camera_number = driver.PvCameraListEx( ctypes.byref(camera_list), 20, None, ctypes.sizeof(tPvCameraInfoEx) )
	#~ print( '{} camera found'.format( camera_number ) )
	#~ print( 'Camera list :\n' )
	#~ for i in range( camera_number ) :
		#~ print( 'Camera {} : {}'.format( i, camera_list[i].UniqueID ) )
	#~ 
	#~ # Release the library
	#~ driver.PvUnInitialize()
	
	
	
	
#~ import cv2
#~ if __name__ == '__main__':
    #~ cv2.namedWindow("Cam", 1)
    #~ capture = cv2.VideoCapture()
    #~ capture.open( 800 )
    #~ while True:
        #~ img = capture.read()[1]
        #~ cv2.imshow("Cam", img)
        #~ if cv2.waitKey(10) == 27: break
    #~ cv2.destroyWindow("Cam")
