extends Camera3D

var udp_server = UDPServer.new()
var port = 12345

var face_position = Vector3.ZERO  # Changed to Vector3
@export var smoothing = 0.9
@export var x_sensitivity = 6.0  # Adjust this to control how much the camera moves
@export var y_sensitivity = 7.0  # Adjust this to control how much the camera moves
@export var z_sensitivity = 4.3

# Fixed rotation target (the point the camera should always look at)
@export var fixed_look_at = Vector3(0, 2, 0)  # Adjust this to set the fixed look-at point

# Limits for position constraints
var min_y_position = -20000.0
var max_y_position = 20000.0

var min_x_position = -20000.0
var max_x_position = 20000.0

var min_z_position = -20000.0
var max_z_position = 20000.0

# Offset the z data
@export var x_offset = -1
@export var y_offset = 0
@export var z_offset = 0
@export var z_offset_on_arrival = 4

# Change fixed angle or dynamic angle
@export var look_at_fixed = true
var gesture = 0
func _ready():
	var err = udp_server.listen(port)
	if err != OK:
		print("Failed to listen on port ", port)
		return
	print("Listening on port ", port)

func _physics_process(delta):
	udp_server.poll()

	var new_global_position = global_position  # Initialize with current position

	if udp_server.is_connection_available():
		var peer = udp_server.take_connection()
		var packet = peer.get_packet()
		var data = packet.get_string_from_utf8().split(",")

		if data.size() == 4:
			# Validate and parse incoming data
			var incoming_x = clamp(float(data[0]), min_x_position, max_x_position)
			var incoming_y = clamp(float(data[1]), min_y_position, max_y_position)
			var incoming_z = clamp(float(data[2]), min_z_position, max_z_position)
			gesture =  bool(int(data[3]))
			print(gesture)
			# Apply offsets and sensitivities
			var target_position = Vector3(
				-incoming_x * x_sensitivity + x_offset,
				incoming_y * y_sensitivity + y_offset,
				(incoming_z + z_offset_on_arrival) * z_sensitivity + z_offset
			)

			# Apply smoothing directly to global_position
			new_global_position = global_position.lerp(target_position, smoothing)


	# Update the global position
	global_position = new_global_position

	if look_at_fixed || gesture:
		# Use look_at_from_position instead of look_at
		look_at(fixed_look_at)
	#else:
	#	rotate(Vector3(0,0,-1),90.0)
		
func _exit_tree():
	udp_server.stop()
