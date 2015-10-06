# -*- coding:utf-8 -*- 


#
# Create a Qt application to display a 3D mesh with OpenGL
#


#
# External dependencies
#
import math
import platform
import sys
import numpy as np
import OpenGL.GL as gl
import PySide as qt
import PySide.QtCore as qtcore
import PySide.QtGui as qtgui
import PySide.QtOpenGL as qtgl
from PyStereoVisionToolkit import Trackball
from PyStereoVisionToolkit import Shader


#
# Customize the Qt OpenGL widget
# to view a point cloud
#
class PointCloudViewer( qtgl.QGLWidget ) :

	#
	# Initialisation
	#
	def __init__( self, parent = None ) :
		
		# Initialise QGLWidget with multisampling enabled and OpenGL 3 core only
		super( PointCloudViewer, self ).__init__( qtgl.QGLFormat( qtgl.QGL.SampleBuffers | qtgl.QGL.NoDeprecatedFunctions ), parent )

		# Track mouse events
		self.setMouseTracking( True )
		
		# Change the widget position and size
		self.setGeometry( 100, 100, 1024, 768 )

		# Trackball for smooth manipulation
		self.trackball = Trackball.Trackball()

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

		# Initialise the projection transformation matrix
		self.SetProjectionMatrix( self.width(), self.height() )

		# Initialise Model-View transformation matrix
		self.modelview_matrix = np.identity( 4, dtype=np.float32 )

		# Position the scene (camera)
		self.modelview_matrix[3,2] = -30.0

		# Load the shaders
		self.shader = Shader.FlatShader()
		gl.glUseProgram( self.shader )

		# Initialise viewing parameters
		self.point_cloud_loaded = False
		self.antialiasing = True
		
		# Vertex array object
		self.vertex_array_id = gl.glGenVertexArrays( 1 )
		gl.glBindVertexArray( self.vertex_array_id )

		# Index buffer object
		indices = np.array( np.arange( 76800 ), dtype=np.uint32 )
		self.index_buffer_id = gl.glGenBuffers( 1 )
		gl.glBindBuffer( gl.GL_ELEMENT_ARRAY_BUFFER, self.index_buffer_id )
		gl.glBufferData( gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW )

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
		vertices[:,1] = -vertices[:,1]
		colors = np.array( colors, dtype=np.float32 ) / 255
		
		# Normalize the model
		center =  0.5 * ( np.amin( vertices, axis = 0 ) + np.amax( vertices, axis = 0 ) )
		radius = np.sqrt(((center - vertices) ** 2).sum(axis = 1)).max()
	#	center = ( 160, 120, 60 )
	#	radius = 200
	#	print center, radius
		vertices -= center
		vertices *= 10.0 / radius

		# Vertex buffer object
		self.vertex_buffer_id = gl.glGenBuffers( 1 )
		gl.glBindBuffer( gl.GL_ARRAY_BUFFER, self.vertex_buffer_id )
		gl.glBufferData( gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW )
		gl.glEnableVertexAttribArray( 0 )
		gl.glVertexAttribPointer( 0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None )

		# Color buffer object
		self.color_buffer_id = gl.glGenBuffers( 1 )
		gl.glBindBuffer( gl.GL_ARRAY_BUFFER, self.color_buffer_id )
		gl.glBufferData( gl.GL_ARRAY_BUFFER, colors.nbytes, colors, gl.GL_STATIC_DRAW )
		gl.glEnableVertexAttribArray( 1 )
		gl.glVertexAttribPointer( 1, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None )

		# Setup model element number
		self.point_cloud_loaded = True

		# Reset the trackball
		self.trackball.Reset()

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
	# Resize the viewport
	#
	def Resize( self, width, height ) :

		# Resize the viewport
		gl.glViewport( 0, 0, width, height )

		# Resize the trackball
		self.trackball.Resize( width, height )

		# Compute perspective projection matrix
		self.SetProjectionMatrix( width, height )

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

		# Senf the MVP matrix to the shader
		gl.glUniformMatrix4fv( gl.glGetUniformLocation( self.shader, "MVP_Matrix" ),
			1, gl.GL_FALSE, np.dot( modelview_matrix, self.projection_matrix ) )

		# Draw the mesh
	#	gl.glDrawElements( gl.GL_POINTS, 76800, gl.GL_UNSIGNED_INT, None )
		gl.glDrawArrays( gl.GL_POINTS, 0, 153600 )

	#
	# resizeGL
	#
	def resizeGL( self, width, height ) :

		# Resize the mesh viewer
		self.Resize( width, height )

	#
	# mousePressEvent
	#
	def mousePressEvent( self, mouseEvent ) :

		# Left button
		if int( mouseEvent.buttons() ) & qtcore.Qt.LeftButton : button = 1

		# Right button
		elif int( mouseEvent.buttons() ) & qtcore.Qt.RightButton : button = 2

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

		# Get the mouse wheel delta for normalisation
		delta = event.delta()

		# Update the trackball
		self.trackball.MouseWheel( delta and delta // abs(delta) )

		# Refresh display
		self.update()

	#
	# Keyboard event
	#
	def keyPressEvent( self, event ) :

		# Escape
		if event.key() == qtcore.Qt.Key_Escape :
			
			# Exit
			self.close()
			
		# A
		elif event.key() == qtcore.Qt.Key_A :

			# Enable / Disable antialiasing
			self.antialiasing = not self.antialiasing
			if self.antialiasing : gl.glEnable( gl.GL_MULTISAMPLE )
			else : gl.glDisable( gl.GL_MULTISAMPLE )

		# I
		elif event.key() == qtcore.Qt.Key_I :
			
			# Print system informations
			print( 'System Informations...' )
			print( '  Python :    {}'.format( platform.python_version() ) )
			print( '  PySide :    {}'.format( qt.__version__ ) )
			print( '  Qt :        {}'.format( qtcore.__version__ ) )

			# Display OpenGL driver informations
			print( 'OpenGL Informations...' )
			print( '  Vendor :    {}'.format( gl.glGetString( gl.GL_VENDOR ).decode( 'UTF-8' ) ) )
			print( '  Renderer :  {}'.format( gl.glGetString( gl.GL_RENDERER ).decode( 'UTF-8' ) ) )
			print( '  Version :   {}'.format( gl.glGetString( gl.GL_VERSION ).decode( 'UTF-8' ) ) )
			print( '  Shader :    {}'.format( gl.glGetString( gl.GL_SHADING_LANGUAGE_VERSION ).decode( 'UTF-8' ) ) )

		# R
		elif event.key() == qtcore.Qt.Key_R :

			# Reset model translation and rotation
			self.trackball.Reset()

		# Unmanaged key
		else : return

		# Refresh display
		self.update()
