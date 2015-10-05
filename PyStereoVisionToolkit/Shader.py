# -*- coding:utf-8 -*- 


#
# Module used to handle OpenGL shaders
#


#
# External dependencies
#
import OpenGL.GL as gl


#
# Compile and load the shader program
#
def LoadShaders( *shaders ) :

	# Create the program
	program = gl.glCreateProgram()

	# Attach the shaders to the program
	for shader in shaders :
		gl.glAttachShader( program, shader )

	# Link the program
	gl.glLinkProgram( program )

	# Check the program
	if not gl.glGetProgramiv( program, gl.GL_LINK_STATUS ) :
		raise RuntimeError( 'Shader program linking failed.\n{}'.format( gl.glGetProgramInfoLog( program ) ) )

	# Detach the shaders from the program
	for shader in shaders :
		gl.glDetachShader( program, shader )

	# Delete the shaders
	for shader in shaders :
		gl.glDeleteShader( shader )

	# Return the program ID
	return program


#
# Compile a shader from source code
#
def CompileShader( shader_source, shader_type ) :

	# Create the shaders
	shader = gl.glCreateShader( shader_type )

	# Load shader source code
	gl.glShaderSource( shader, shader_source )

	# Compile the shader
	gl.glCompileShader( shader )

	# Check the shader
	if not gl.glGetShaderiv( shader, gl.GL_COMPILE_STATUS ) :
		raise RuntimeError( 'Shader compilation failed.\n{}'.format( gl.glGetShaderInfoLog( shader ) ) )

	# Return the shader ID
	return shader


#
# Flat shader
#
class FlatShader( int ) :

	#
	# Initialisation
	#
	def __new__( cls ) :

		# Load a flat shading program
		program = LoadShaders( CompileShader( cls.flat_shader_vertex, gl.GL_VERTEX_SHADER ),
			CompileShader( cls.flat_shader_fragment, gl.GL_FRAGMENT_SHADER ) )
		
		# Register the program ID
		return super( FlatShader, cls ).__new__( cls, program )

	#
	# Flat shading - Vertex shader
	#
	flat_shader_vertex = '''#version 330 core

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
	# Flat shading - Fragment shader
	#
	flat_shader_fragment = '''#version 330 core

		flat in vec4 FragColor;

		out vec4 Color;

		void main( void ) {

			Color = FragColor;

		}'''


