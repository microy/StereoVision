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
import CvViewer

# Camera serial numbers
camera_1_id = '50-0503323406'
camera_2_id = '50-0503326223'

# Create a command line argument parser
parser = argparse.ArgumentParser( description='Display images from AVT cameras' )
parser.add_argument( 'Number', help='Camera number (1, 2, 12 )' )

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
	CvViewer.VmbViewer( camera_1_id ).LiveDisplay()

# View camera 2
elif args.Number == '2' :
	CvViewer.VmbViewer( camera_2_id ).LiveDisplay()
	
# View both cameras
elif args.Number == '12' :
	CvViewer.VmbStereoViewer( camera_1_id, camera_2_id ).LiveDisplay()
	
# Vimba shutdown
Vimba.VmbShutdown()
