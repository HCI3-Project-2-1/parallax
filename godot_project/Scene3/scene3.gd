extends Camera3D

var udp_server = UDPServer.new()
var port = 12345

var face_position = Vector3.ZERO  # Changed to Vector3
var smoothing = 1  # Reduced smoothing for more responsive movement
var sensitivity = 20.0  # Adjust this to control how much the camera moves
var z_sensitivity = 4.0
# Fixed rotation target (the point the camera should always look at)
var fixed_look_at = Vector3(0, 2, 0)  # Adjust this to set the fixed look-at point


# Limit for minimum and maximum y position (to constrain vertical movement)
var min_y_position = 1.0  # Set a small positive value to prevent going below ground level
var max_y_position = 20.0  # You can adjust the upper limit if necessary

# Limit for minimum and maximum X position (to constrain horizontal movement)
var min_x_position = -20.0  # Lower bound for X position
var max_x_position = 20.0   # Upper bound for X position
# Limit for minimum and maximum X position (to constrain horizontal movement)
var min_z_position = -200.0  # Lower bound for X position
var max_z_position = 200.0   # Upper bound for X position
#Offset the z data
var z_offset = 3
# Change fixed angle or dynamic angle
@export var look_at_fixed = false

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
			print("Received data: ", data)  # Debug print
			var new_position = Vector3(-float(data[0]), float(data[1]), float(data[2])+z_offset)
			face_position = face_position.lerp(new_position, smoothing)

	# Adjust position in X, Y, and Z axes based on UDP data
	var target_position = Vector3(
		float(face_position.x * sensitivity),
		max(float(face_position.y * sensitivity + 4), min_y_position),
		float(face_position.z * z_sensitivity)
	)

	# Lerp the global position
	global_position = global_position.lerp(target_position, smoothing)

	# Clamp the X, Y, and Z positions to their respective limits
	global_position.x = clamp(global_position.x, min_x_position, max_x_position)
	global_position.y = clamp(global_position.y, min_y_position, max_y_position)
	global_position.z = clamp(global_position.z, min_z_position, max_z_position)

	if look_at_fixed:
		look_at(Vector3.ZERO)

func _exit_tree():
	udp_server.stop()
