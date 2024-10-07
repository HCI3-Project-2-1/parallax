extends Camera3D

var udp_server = UDPServer.new()
var port = 12345

var face_position = Vector2.ZERO
var smoothing = 0.9
var sensitivity = 5.0  # Adjust this to control how much the camera moves

# Fixed rotation target (the point the camera should always look at)
var fixed_look_at = Vector3(0, 2, 0)  # Adjust this to set the fixed look-at point

# Speed of the camera movement
var move_speed = 5.0  # Speed at which the camera moves

# Limit for minimum Y position (to prevent negative Y values)
var min_y_position = -20.0  # Set a small positive value to prevent going below ground level

# Optional maximum Y position (if needed)
var max_y_position = 20.0  # You can adjust the upper limit if necessary

# Limit for minimum and maximum X position (to constrain horizontal movement)
var min_x_position = -20.0  # Lower bound for X position
var max_x_position = 20.0   # Upper bound for X position

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
		if data.size() == 2:
			#print("Received data: ", data)  # Debug print
			var new_position = Vector2(-float(data[0]), float(data[1]))
			face_position = face_position.lerp(new_position, smoothing)

	# Adjust position in X and Y axes based on UDP data
	var target_position_x = float(face_position.x * sensitivity)
	
	# Prevent Y from going below ground, cast to float to avoid type issues
	var target_position_y = float(max(face_position.y * sensitivity, min_y_position))

	# Keep Z position constant to ensure the camera stays on the Z-axis
	global_position.x = lerp(float(global_position.x), target_position_x, smoothing)
	global_position.y = lerp(float(global_position.y), target_position_y, smoothing)

	# Clamp the X and Y positions to their respective limits
	global_position.x = clamp(global_position.x, min_x_position, max_x_position)
	global_position.y = clamp(global_position.y, min_y_position, max_y_position)

	# Ensure the camera remains on the Z-axis by not modifying the Z position
	# If you need to set a specific Z position, uncomment the following line:
	# global_position.z = desired_z_position

	# Make the camera always look at the fixed point (0, 0, 0)
	look_at(fixed_look_at)

	# Handle movement input (WASD)
	_handle_movement(delta)

	#print("Camera position: ", global_position)  # Debug print

func _exit_tree():
	udp_server.stop()

# Function to handle movement based on WASD keys
func _handle_movement(delta):
	var move_direction = Vector3()

	# Move forward (W) and backward (S)
	if Input.is_action_pressed("move_forward"):
		move_direction.z -= 1
	if Input.is_action_pressed("move_backward"):
		move_direction.z += 1

	# Normalize direction and apply speed
	move_direction = move_direction.normalized() * move_speed * delta
	
	# Apply movement in the local space (use translation instead of global_position)
	translate(move_direction)
