#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images from AVT cameras
# using the AVT Vimba SDK
#


# External dependencies
import argparse
import sys
import Vimba
import Viewer

# Camera serial numbers
camera_1_id = '50-0503323406'
camera_2_id = '50-0503326223'

# Create a command line argument parser
parser = argparse.ArgumentParser( description='Display images from AVT cameras', usage='%(prog)s Number' )
parser.add_argument( 'Number', nargs='?', help='Number of the camera to display (1, 2, or 12 )' )

# Process command line parameters
args = parser.parse_args()

# Print help and exit if a wrong parameter is given
if args.Number not in [ '1', '2', '12' ] :
	parser.print_help()
	sys.exit()
	
# Vimba initialization
Vimba.VmbStartup()

# View camera 1
if args.Number == '1' :

	# Camera connection
	camera = Vimba.VmbCamera( camera_1_id )

	# Start image acquisition
	Viewer.LiveDisplay( camera )

	# Print camera statistics
	camera.PrintStats()

	# Camera disconnection
	camera.Disconnect()
	
# View camera 2
elif args.Number == '2' :
	
	# Camera connection
	camera = Vimba.VmbCamera( camera_2_id )

	# Start image acquisition
	Viewer.LiveDisplay( camera )

	# Print camera statistics
	camera.PrintStats()

	# Camera disconnection
	camera.Disconnect()
	
# View both cameras
elif args.Number == '12' :
	
	# Camera connection
	camera_1 = Vimba.VmbCamera( camera_1_id )
	camera_2 = Vimba.VmbCamera( camera_2_id )

	# Start image acquisition
	Viewer.LiveDisplayStereo( camera_1, camera_2 )

	# Print camera statistics
	camera_1.PrintStats()
	camera_2.PrintStats()
	
	# Close the cameras
	camera_1.Disconnect()
	camera_2.Disconnect()

# Vimba shutdown
Vimba.VmbShutdown()
