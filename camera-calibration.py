#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to calibrate a camera
# from given chessboard images
#


#
# External dependencies
#
import argparse
import Calibration


# Create a command line argument parser
parser = argparse.ArgumentParser( description='Calibrate a camera' )
parser.add_argument( 'input_files', help='Image files used for the calibration' )
parser.add_argument( '-p', '--pattern', nargs=2, metavar=('x', 'y'), help='Size of the chessboard pattern to search' )
parser.add_argument( '-d', '--display', action='store_true', help='Display the chessboard on each image' )

# Process command line parameters
args = parser.parse_args()

# Change chessboard pattern size
if args.pattern :
	Calibration.pattern_size = ( int(args.pattern[0]), int(args.pattern[1]) )

# Launch calibration
Calibration.CameraCalibration( args.input_files, args.display )
