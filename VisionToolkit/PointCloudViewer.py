# -*- coding:utf-8 -*-


#
# Create a Qt application to display a 3D mesh with OpenGL
#


#
# External dependencies
#
import math
import numpy as np
import OpenGL.GL as gl
import PySide as Qt
from PySide import QtCore
from PySide import QtOpenGL
import VisionToolkit as vtk


#
# Customize the Qt OpenGL widget
# to view a point cloud
#
class PointCloudViewer( QtOpenGL.QGLWidget ) :

	#
	# Vertex shader
	#
	vertex_shader_source = '''#version 330 core

		layout (location = 0) in vec4 Vertex;
		layout (location = 1) in vec3 Color;

		uniform mat4 MVP_Matrix;

		flat out vec4 FragColor;

		void main( void ) {

			FragColor.xyz = Color;
			FragColor.a = 1.0;

			gl_Position = MVP_Matrix * Vertex;
		}'''

	#
	# Fragment shader
	#
	fragment_shader_source = '''#version 330 core

		flat in vec4 FragColor;

		out vec4 Color;

		void main( void ) {

			Color = FragColor;

		}'''

	#
	# Initialisation
	#
	def __init__( self, parent = None ) :

		# Initialise QGLWidget with multisampling enabled and OpenGL 3 core only
		super( PointCloudViewer, self ).__init__( QtOpenGL.QGLFormat( QtOpenGL.QGL.SampleBuffers | QtOpenGL.QGL.NoDeprecatedFunctions ), parent )

		# Track mouse events
		self.setMouseTracking( True )

		# Change the widget position and size
		self.setGeometry( 100, 100, 1024, 768 )

		# Trackball for smooth manipulation
		self.trackball = vtk.Trackball()

		# Set the Escape key to close the application
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Escape ), self ).activated.connect( self.close )

		# Set the R key to reset the view
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_R ), self ).activated.connect( self.trackball.Reset )

	#
	# initializeGL
	#
	def initializeGL( self ) :

		# Initialise the trackball
		self.trackball.Initialise( self.width(), self.height() )

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
		shader = gl.glCreateProgram()
		gl.glAttachShader( shader, vertex_shader )
		gl.glAttachShader( shader, fragment_shader )
		gl.glLinkProgram( shader )
		gl.glUseProgram( shader )
		gl.glDetachShader( shader, vertex_shader )
		gl.glDetachShader( shader, fragment_shader )
		gl.glDeleteShader( vertex_shader )
		gl.glDeleteShader( fragment_shader )

		# Initialise the projection transformation matrix
		self.SetProjectionMatrix( self.width(), self.height() )

		# Initialise Model-View transformation matrix
		self.modelview_matrix = np.identity( 4, dtype=np.float32 )

		# Position the scene (camera)
		self.modelview_matrix[3,2] = -30.0

		# Initialise viewing parameters
		self.point_cloud_loaded = False
		self.antialiasing = True

		# Vertex array object
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

	#
	# Load the mesh for display
	#
	def LoadPointCloud( self, coordinates, colors ) :

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

	#
	# Close the mesh
	#
	def Close( self ) :

		# Need to initialise ?
		if not self.point_cloud_loaded : return

		# Delete buffer objects
		gl.glDeleteBuffers( 1, np.array([ self.vertex_buffer_id ]) )
		gl.glDeleteBuffers( 1, np.array([ self.color_buffer_id ]) )

		# Initialise the model parameters
		self.point_cloud_loaded = False

	#
	# Compute a perspective matrix
	#
	def SetProjectionMatrix( self, width, height ) :

		fovy, aspect, near, far = 45.0, float(width)/height, 0.1, 100.0
		f = math.tan( math.pi * fovy / 360.0 )
		self.projection_matrix = np.identity( 4, dtype=np.float32 )
		self.projection_matrix[0,0] = 1.0 / (f * aspect)
		self.projection_matrix[1,1] = 1.0 / f
		self.projection_matrix[2,2] = - (far + near) / (far - near)
		self.projection_matrix[2,3] = - 1.0
		self.projection_matrix[3,2] = - 2.0 * near * far / (far - near)

	#
	# paintGL
	#
	def paintGL( self ) :

		# Clear all pixels and depth buffer
		gl.glClear( gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT )

		# Nothing to display
		if not self.point_cloud_loaded : return

		# Apply trackball transformation to the initial model-view matrix
		modelview_matrix = np.dot( self.trackball.transformation, self.modelview_matrix )

		# Send the MVP matrix to the shader
		gl.glUniformMatrix4fv( gl.glGetUniformLocation( self.shader, "MVP_Matrix" ),
			1, gl.GL_FALSE, np.dot( modelview_matrix, self.projection_matrix ) )

		# Draw the mesh
		gl.glDrawArrays( gl.GL_POINTS, 0, 153600 )

	#
	# resizeGL
	#
	def resizeGL( self, width, height ) :

		# Resize the viewport
		gl.glViewport( 0, 0, width, height )

		# Resize the trackball
		self.trackball.Resize( width, height )

		# Compute perspective projection matrix
		self.SetProjectionMatrix( width, height )

	#
	# mousePressEvent
	#
	def mousePressEvent( self, mouseEvent ) :

		# Left button
		if int( mouseEvent.buttons() ) & QtCore.Qt.LeftButton : button = 1

		# Right button
		elif int( mouseEvent.buttons() ) & QtCore.Qt.RightButton : button = 2

		# Unmanaged
		else : return

		# Update the trackball
		self.trackball.MousePress( [ mouseEvent.x(), mouseEvent.y() ], button )

	#
	# mouseReleaseEvent
	#
	def mouseReleaseEvent( self, mouseEvent ) :

		# Update the trackball
		self.trackball.MouseRelease()

	#
	# mouseMoveEvent
	#
	def mouseMoveEvent( self, mouseEvent ) :

		# Update the trackball
		if self.trackball.MouseMove( mouseEvent.x(), mouseEvent.y() ) :

			# Refresh display
			self.update()

	#
	# wheelEvent
	#
	def wheelEvent( self, event ) :

		# Get the mouse wheel delta
		delta = event.delta()

		# Normalize the wheel delta
		delta = delta and delta // abs( delta )

		# Update the trackball
		self.trackball.MouseWheel( delta )

		# Refresh display
		self.update()
