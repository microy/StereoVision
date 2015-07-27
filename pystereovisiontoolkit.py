#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture, and calibrate stereo cameras
#


#
# External dependencies
#
import argparse
import glob
import Calibration
import Viewer


#
# Command line argument parser
#
parser = argparse.ArgumentParser( description='Camera calibration toolkit.' )
parser.add_argument( '-live', action='store_true', help='Stereo camera live display' )
parser.add_argument( '-rows', action='store', default=15, help='Number of rows in the chessboard pattern' )
parser.add_argument( '-cols', action='store', default=10, help='Number of columns in the chessboard pattern' )
parser.add_argument( '-debug', action='store_true', help='Display the chessboard on each image' )
parser.add_argument( '-mono', action='store', help='Image files for mono camera calibration' )
parser.add_argument( '-stereo', action='store_true', help='Stereo camera calibration' )
parser.add_argument( '-output', action='store', help='Save results in a JSON file' )
args = parser.parse_args()


#
# Calibration pattern setup
#
Calibration.pattern_size = ( int(args.rows), int(args.cols) )


#
# Stereo camera live capture
#
if args.live :

	Viewer.VmbStereoViewer()


#
# Mono camera calibration
#
elif args.mono :
	
	calibration = Calibration.CameraCalibration( sorted( glob.glob( args.mono ) ), args.output, args.debug )
	

#
# Stereo camera calibration
#
elif args.stereo :
	
	Calibration.StereoCameraCalibration( args.debug )

