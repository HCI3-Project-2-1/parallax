extends Camera3D

var udp_server = UDPServer.new()
var port = 12345

var face_position = Vector3.ZERO  # Changed to Vector3
@export var smoothing = 1  
@export var x_sensitivity = 6.0  # Adjust this to control how much the camera moves
@export var y_sensitivity = 7.0  # Adjust this to control how much the camera moves
@export var z_sensitivity = 4.3

# Fixed rotation target (the point the camera should always look at)
var fixed_look_at = Vector3(0, 2, 0)  # Adjust this to set the fixed look-at point


# Limit for minimum and maximum y position (to constrain vertical movement)
var min_y_position = -20000.0  # Set a small positive value to prevent going below ground level
var max_y_position = 20000.0  # You can adjust the upper limit if necessary

# Limit for minimum and maximum X position (to constrain horizontal movement)
var min_x_position = -20000.0  # Lower bound for X position
var max_x_position = 20000.0   # Upper bound for X position
# Limit for minimum and maximum X position (to constrain horizontal movement)
var min_z_position = -20000.0  # Lower bound for X position
var max_z_position = 20000.0   # Upper bound for X position
#Offset the z data
@export var x_offset = -1
@export var y_offset = 0
@export var z_offset = 0
@export var z_offset_on_arrival = 4
# Change fixed angle or dynamic angle
@export var look_at_fixed = true

func _ready():
	var err = udp_server.listen(port)
	if err != OK:
		print("Failed to listen on port ", port)
		return
	print("Listening on port ", port)

func _process(delta):
	udp_server.poll()

	if udp_server.is_connection_available():
		var peer = udp_server.take_connection()
		var packet = peer.get_packet()
		var data = packet.get_string_from_utf8().split(",")
		if data.size() == 3:
			# Map the axes according to the new requirements
			var new_position = Vector3(-float(data[0]), float(data[1]), float(data[2])+ z_offset_on_arrival)
			face_position = face_position.lerp(new_position, smoothing)
	if look_at_fixed:
		look_at(Vector3.DOWN)
	
	# Adjust position in X, Y, and Z axes based on UDP data
	var target_position = Vector3(
		float(face_position.x * x_sensitivity+ x_offset),  # X axis for right movement
		float(face_position.y * y_sensitivity+ y_offset),  # Y axis from data
		float(face_position.z * z_sensitivity+ z_offset)  # Z axis for height
	)

	# Lerp the global position
	global_position = global_position.lerp(target_position, smoothing)

	# Clamp the X, Y, and Z positions to their respective limits
	global_position.x = clamp(global_position.x, min_x_position, max_x_position)
	global_position.y = clamp(global_position.y, min_y_position, max_y_position)
	global_position.z = clamp(global_position.z, min_z_position, max_z_position)



func _exit_tree():
	udp_server.stop()
