# -*- coding:utf-8 -*-


#
# Implement a trackball to manipulate the 3D model inside the OpenGL frame.
#


#
# Inspired from :
#
#       - Nate Robins' Programs
#         http://www.xmission.com/~nate
#
#       - NeHe Productions - ArcBall Rotation Tutorial
#         http://nehe.gamedev.net
#


#
# External dependencies
#
import math
import numpy as np


#
# Create a trackball class for smooth object transformation
#
class Trackball( object ) :

	#
	# Initialisation
	#
	def Initialise( self, width, height ) :

		# Window size
		self.width = width
		self.height = height

		# Button pressed
		self.button = 0

		# Mouse position
		self.previous_mouse_position = [ 0, 0 ]

		# Tranformation matrix
		self.transformation = np.identity( 4, dtype=np.float32 )

	#
	# Reset the current transformation
	#
	def Reset( self ) :

		# Reset the tranformation matrix
		self.transformation = np.identity( 4, dtype=np.float32 )

	#
	# Resize the viewing parameters
	#
	def Resize( self, width, height ) :

		# Change window size
		self.width = width
		self.height = height

	#
	# Handle when a mouse button is pressed
	#
	def MousePress( self, mouse_position, button ) :

		# Record mouse position
		self.previous_mouse_position = mouse_position

		# Record button pressed
		self.button = button

	#
	# Handle when a mouse button is released
	#
	def MouseRelease( self ) :

		# Mouse button release
		self.button = 0

	#
	# Handle when the mouse wheel is used
	#
	def MouseWheel( self, delta ) :

		# Compute the Z-translation
		translation = np.zeros( 3 )
		translation[2] -= delta * 2.0

		# Project the translation vector to the object space
		translation = np.dot( self.transformation[:3,:3], translation )

		# Translate the transformation matrix
		m = self.transformation
		m[3] = m[0] * translation[0] + m[1] * translation[1] + m[2] * translation[2] + m[3]

	#
	# Handle when the mouse is moved
	#
	def MouseMove( self, mouse_x, mouse_y ) :

		# Rotation
		if self.button == 1 :

			# Map the mouse positions
			previous_position = self.TrackballMapping( self.previous_mouse_position )
			current_position = self.TrackballMapping( [ mouse_x, mouse_y ] )

			# Project the rotation axis to the object space
			rotation_axis = np.dot( self.transformation[:3,:3], np.cross( previous_position, current_position ) )

			# Rotation angle
			rotation_angle = math.sqrt( ((current_position - previous_position)**2).sum() ) * 2.0

			# Create a rotation matrix according to the given angle and axis
			c, s = math.cos( rotation_angle ), math.sin( rotation_angle )
			n = math.sqrt( (rotation_axis**2).sum() )
			if n == 0 : n = 1.0
			rotation_axis /= n
			x, y, z = rotation_axis
			cx, cy, cz = (1 - c) * x, (1 - c) * y, (1 - c) * z
			R = np.array([ [   cx*x + c, cy*x - z*s, cz*x + y*s, 0],
					[ cx*y + z*s,   cy*y + c, cz*y - x*s, 0],
					[ cx*z - y*s, cy*z + x*s,   cz*z + c, 0],
					[          0,          0,          0, 1] ], dtype=np.float32 ).T

			# Rotate the transformation matrix
			self.transformation = np.dot( R, self.transformation )

		# XY translation
		elif self.button ==  2 :

			# Compute the XY-translation
			translation = np.zeros( 3 )
			translation[0] -= (self.previous_mouse_position[0] - mouse_x)*0.02
			translation[1] += (self.previous_mouse_position[1] - mouse_y)*0.02

			# Project the translation vector to the object space
			translation = np.dot( self.transformation[:3,:3], translation )

			# Translate the transformation matrix
			m = self.transformation
			m[3] = m[0] * translation[0] + m[1] * translation[1] + m[2] * translation[2] + m[3]

		# No update
		else : return False

		# Save the mouse position
		self.previous_mouse_position = [ mouse_x, mouse_y ]

		# Require a display update
		return True

	#
	# Map the mouse position onto a unit sphere
	#
	def TrackballMapping( self, mouse_position ) :

		v = np.zeros( 3 )
		v[0] = ( 2.0 * mouse_position[0] - self.width ) / self.width
		v[1] = ( self.height - 2.0 * mouse_position[1] ) / self.height
		d = math.sqrt(( v**2 ).sum())
		if d > 1.0 : d = 1.0
		v[2] = math.cos( math.pi / 2.0 * d )
		return v / math.sqrt(( v**2 ).sum())
