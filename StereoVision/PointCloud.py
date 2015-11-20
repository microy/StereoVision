# -*- coding:utf-8 -*-

#
# Create a Qt application to display a 3D point cloud with OpenGL
#

# Inspired from :
#  - Nate Robins' Programs (http://www.xmission.com/~nate)
#  - NeHe Productions (http://nehe.gamedev.net)

# External dependencies
import math
import numpy as np
import OpenGL.GL as gl
from PySide import QtCore
from PySide import QtGui
from PySide import QtOpenGL

# Customize the Qt OpenGL widget to display a point cloud
class PointCloudViewer( QtOpenGL.QGLWidget ) :

	# Signal sent to update the point cloud in the widget
	update_pointcloud = QtCore.Signal( np.ndarray, np.ndarray )

	# Vertex shader
	vertex_shader_source = '''#version 330 core
		layout (location = 0) in vec4 Vertex;
		layout (location = 1) in vec3 Color;
		uniform mat4 MVP_Matrix;
		out vec4 FragColor;
		void main( void ) {
			FragColor.xyz = Color;
			FragColor.a = 1.0;
			gl_Position = MVP_Matrix * Vertex;
		}'''

	# Fragment shader
	fragment_shader_source = '''#version 330 core
		in vec4 FragColor;
		out vec4 Color;
		void main( void ) {
			Color = FragColor;
		}'''

	# Initialize the Qt widget
	def __init__( self, parent = None ) :
		# Initialise QGLWidget with multisampling enabled and OpenGL 3 core only
		super( PointCloudViewer, self ).__init__( QtOpenGL.QGLFormat( QtOpenGL.QGL.SampleBuffers | QtOpenGL.QGL.NoDeprecatedFunctions ), parent )
		# Connect the signal to update the point cloud
		self.update_pointcloud.connect( self.UpdatePointCloud )
		# Set the window title
		self.setWindowTitle( 'Point Cloud' )
		# Track mouse events
		self.setMouseTracking( True )
		# Change the widget position and size
		self.setGeometry( 100, 100, 1024, 768 )
		# Button pressed
		self.button = 0
		# Mouse position
		self.previous_mouse_position = [ 0, 0 ]
		# Tranformation matrix
		self.transformation = np.identity( 4, dtype=np.float32 )
		# Set the Escape key to close the application
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Escape ), self ).activated.connect( self.close )
		# Set the R key to reset the view
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_R ), self ).activated.connect( self.Reset )

	# Initialize OpenGL
	def initializeGL( self ) :
		# Default background color
		gl.glClearColor( 1, 1, 1, 1 )
		# Enable depth test
		gl.glEnable( gl.GL_DEPTH_TEST )
		# Enable face culling
		gl.glEnable( gl.GL_CULL_FACE )
		# Enable blending function
		gl.glEnable( gl.GL_BLEND )
		gl.glBlendFunc( gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA )
		# Enable multisampling (antialiasing)
		gl.glEnable( gl.GL_MULTISAMPLE )
		# Change point size
		gl.glPointSize( 5.0 )
		# Compile the shaders
		vertex_shader = gl.glCreateShader( gl.GL_VERTEX_SHADER )
		gl.glShaderSource( vertex_shader, self.vertex_shader_source )
		gl.glCompileShader( vertex_shader )
		fragment_shader = gl.glCreateShader( gl.GL_FRAGMENT_SHADER )
		gl.glShaderSource( fragment_shader, self.fragment_shader_source )
		gl.glCompileShader( fragment_shader )
		# Load the shaders
		self.shader = gl.glCreateProgram()
		gl.glAttachShader( self.shader, vertex_shader )
		gl.glAttachShader( self.shader, fragment_shader )
		gl.glLinkProgram( self.shader )
		gl.glUseProgram( self.shader )
		gl.glDetachShader( self.shader, vertex_shader )
		gl.glDetachShader( self.shader, fragment_shader )
		gl.glDeleteShader( vertex_shader )
		gl.glDeleteShader( fragment_shader )
		# Initialise the projection transformation matrix
		self.SetProjectionMatrix()
		# Initialise Model-View transformation matrix
		self.modelview_matrix = np.identity( 4, dtype=np.float32 )
		# Position the scene (camera)
		self.modelview_matrix[3,2] = -30.0
		# Initialise viewing parameters
		self.point_cloud_loaded = False
		# Vertex array object
		self.vertex_array_id = gl.glGenVertexArrays( 1 )
		gl.glBindVertexArray( self.vertex_array_id )
		# Vertex buffer object
		self.vertex_buffer_id = gl.glGenBuffers( 1 )
	#	gl.glBindBuffer( gl.GL_ARRAY_BUFFER, self.vertex_buffer_id )
	#	gl.glBufferData( gl.GL_ARRAY_BUFFER, 921600, None, gl.GL_STATIC_DRAW )
	#	gl.glEnableVertexAttribArray( 0 )
	#	gl.glVertexAttribPointer( 0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None )
		# Color buffer object
		self.color_buffer_id = gl.glGenBuffers( 1 )
	#	gl.glBindBuffer( gl.GL_ARRAY_BUFFER, self.color_buffer_id )
	#	gl.glBufferData( gl.GL_ARRAY_BUFFER, 921600, None, gl.GL_STATIC_DRAW )
	#	gl.glEnableVertexAttribArray( 1 )
	#	gl.glVertexAttribPointer( 1, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None )

	# Load the point cloud for display
	def UpdatePointCloud( self, coordinates, colors ) :
		# Close previous mesh
		self.Close()
		coordinates = coordinates.reshape(-1, 3)
		colors = colors.reshape(-1, 3)
	#	mask = coordinates[:, 2] > coordinates[:, 2].min()+10
	#	coordinates = coordinates[ mask ]
	#	colors = colors[ mask ]
	#	mask = coordinates[:, 2] < coordinates[:, 2].max()-10
	#	coordinates = coordinates[ mask ]
	#	colors = colors[ mask ].astype( np.float32 ) / 255
		# Cast input data (required for OpenGL)
		vertices = np.array( coordinates, dtype=np.float32 )
	#	vertices[:,1] = -vertices[:,1]
	#	colors = np.array( colors, dtype=np.float32 ) / 255
		# Normalize the model
		center =  0.5 * ( np.amin( vertices, axis = 0 ) + np.amax( vertices, axis = 0 ) )
		radius = np.sqrt(((center - vertices) ** 2).sum(axis = 1)).max()
	#	center = ( 160, 120, 60 )
	#	radius = 200
	#	print center, radius
		vertices -= center
		vertices *= 10.0 / radius
		gl.glBindVertexArray( self.vertex_array_id )
		# Vertex buffer object
	#	self.vertex_buffer_id = gl.glGenBuffers( 1 )
		gl.glBindBuffer( gl.GL_ARRAY_BUFFER, self.vertex_buffer_id )
		gl.glBufferData( gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW )
		gl.glEnableVertexAttribArray( 0 )
		gl.glVertexAttribPointer( 0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None )
	#	gl.glBindBuffer( gl.GL_ARRAY_BUFFER, self.vertex_buffer_id )
	#	gl.glBufferSubData( gl.GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices )
		# Color buffer object
	#	self.color_buffer_id = gl.glGenBuffers( 1 )
		gl.glBindBuffer( gl.GL_ARRAY_BUFFER, self.color_buffer_id )
		gl.glBufferData( gl.GL_ARRAY_BUFFER, colors.nbytes, colors, gl.GL_STATIC_DRAW )
		gl.glEnableVertexAttribArray( 1 )
		gl.glVertexAttribPointer( 1, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None )
	#	gl.glBindBuffer( gl.GL_ARRAY_BUFFER, self.color_buffer_id )
	#	gl.glBufferSubData( gl.GL_ARRAY_BUFFER, 0, colors.nbytes, colors )
		# Setup model element number
		self.point_cloud_loaded = True
		# Refresh display
		self.update()

	# Display the point cloud
	def paintGL( self ) :
		# Clear all pixels and depth buffer
		gl.glClear( gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT )
		# Nothing to display
		if not self.point_cloud_loaded : return
		# Apply trackball transformation to the initial model-view matrix
		modelview_matrix = np.dot( self.transformation, self.modelview_matrix )
		# Send the MVP matrix to the shader
		gl.glUniformMatrix4fv( gl.glGetUniformLocation( self.shader, b'MVP_Matrix' ),
			1, gl.GL_FALSE, np.dot( modelview_matrix, self.projection_matrix ) )
		# Draw the mesh
		gl.glDrawArrays( gl.GL_POINTS, 0, 153600 )

	# Resize the Qt widget and the OpenGL viewport
	def resizeGL( self, width, height ) :
		# Resize the viewport
		gl.glViewport( 0, 0, width, height )
		# Compute perspective projection matrix
		self.SetProjectionMatrix()

	# Close the point cloud
	def Close( self ) :
		# Need to initialise ?
		if not self.point_cloud_loaded : return
		# Delete buffer objects
		gl.glDeleteBuffers( 1, np.array([ self.vertex_buffer_id ]) )
		gl.glDeleteBuffers( 1, np.array([ self.color_buffer_id ]) )
		# Initialise the model parameters
		self.point_cloud_loaded = False

	# Reset the current transformation matrix
	def Reset( self ) :
		self.transformation = np.identity( 4, dtype=np.float32 )

	# Mouse button pressed
	def mousePressEvent( self, event ) :
		# Left button
		if int( event.buttons() ) & QtCore.Qt.LeftButton : self.button = 1
		# Right button
		elif int( event.buttons() ) & QtCore.Qt.RightButton : self.button = 2
		# Unmanaged
		else : return
		# Record mouse position
		self.previous_mouse_position = [ event.x(), event.y() ]

	# Mouse button released
	def mouseReleaseEvent( self, _ ) :
		self.button = 0

	# Mouse move
	def mouseMoveEvent( self, event ) :
		# Get mouse position
		mouse_x, mouse_y =  event.x(), event.y()
		# Rotation
		if self.button == 1 :
			# Map the mouse positions
			previous_position = self.TrackballMapping( self.previous_mouse_position )
			current_position = self.TrackballMapping( [ mouse_x, mouse_y ] )
			# Project the rotation axis to the object space
			rotation_axis = np.dot( self.transformation[:3,:3], np.cross( previous_position, current_position ) )
			# Rotation angle
			rotation_angle = math.sqrt( ( ( current_position - previous_position ) ** 2 ).sum() ) * 2.0
			# Create a rotation matrix according to the given angle and axis
			c, s = math.cos( rotation_angle ), math.sin( rotation_angle )
			n = math.sqrt( ( rotation_axis ** 2 ).sum() )
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
			translation[0] -= ( self.previous_mouse_position[0] - mouse_x ) * 0.02
			translation[1] += ( self.previous_mouse_position[1] - mouse_y ) * 0.02
			# Project the translation vector to the object space
			translation = np.dot( self.transformation[:3,:3], translation )
			# Translate the transformation matrix
			m = self.transformation
			m[3] = m[0] * translation[0] + m[1] * translation[1] + m[2] * translation[2] + m[3]
		# No update
		else : return
		# Save the mouse position
		self.previous_mouse_position = [ mouse_x, mouse_y ]
		# Refresh display
		self.update()

	# Wheel action
	def wheelEvent( self, event ) :
		# Get the mouse wheel delta
		delta = event.delta()
		# Normalize the wheel delta
		delta = delta and delta // abs( delta )
		# Compute the Z-translation
		translation = np.zeros( 3 )
		translation[2] -= delta * 2.0
		# Project the translation vector to the object space
		translation = np.dot( self.transformation[:3,:3], translation )
		# Translate the transformation matrix
		m = self.transformation
		m[3] = m[0] * translation[0] + m[1] * translation[1] + m[2] * translation[2] + m[3]
		# Refresh display
		self.update()

	# Compute a perspective matrix
	def SetProjectionMatrix( self ) :
		fovy, aspect, near, far = 45.0, float( self.width() ) / self.height(), 0.1, 100.0
		f = math.tan( math.pi * fovy / 360.0 )
		self.projection_matrix = np.identity( 4, dtype=np.float32 )
		self.projection_matrix[0,0] = 1.0 / (f * aspect)
		self.projection_matrix[1,1] = 1.0 / f
		self.projection_matrix[2,2] = - (far + near) / (far - near)
		self.projection_matrix[2,3] = - 1.0
		self.projection_matrix[3,2] = - 2.0 * near * far / (far - near)

	# Map the mouse position onto a unit sphere
	def TrackballMapping( self, mouse_position ) :
		v = np.zeros( 3 )
		v[0] = ( 2.0 * mouse_position[0] - self.width() ) / self.width()
		v[1] = ( self.height() - 2.0 * mouse_position[1] ) / self.height()
		d = math.sqrt( ( v ** 2 ).sum() )
		if d > 1.0 : d = 1.0
		v[2] = math.cos( math.pi / 2.0 * d )
		return v / math.sqrt( ( v ** 2 ).sum() )
