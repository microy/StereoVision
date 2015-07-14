#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to calibrate a pair of cameras
# from given chessboard images
#


#
# External dependencies
#
import argparse
import Calibration


# Create a command line argument parser
parser = argparse.ArgumentParser( description='Calibrate a pair of cameras' )
parser.add_argument( 'left_camera_input_files', help='Image files from the left camera' )
parser.add_argument( 'right_camera_input_files', help='Image files from the right camera' )
parser.add_argument( '-r', action='store', metavar='rows', default=10, help='Number of rows in the chessboard' )
parser.add_argument( '-c', action='store', metavar='columns', default=15, help='Number of columns in the chessboard' )
parser.add_argument( '-g', action='store_true', default=False, help='Asymetric circles grid pattern' )
parser.add_argument( '-d', action='store_true', default=False, help='Display the chessboard on each image' )

# Process command line parameters
args = parser.parse_args()

# Setup pattern type
if args.g :
	Calibration.pattern_type = 'CirclesGrid'

# Setup pattern size
Calibration.pattern_size = ( int(args.r), int(args.c) )

# Launch calibration
Calibration.StereoCameraCalibration( args.left_camera_input_files, args.right_camera_input_files, args.d )
