extends Camera3D

var udp_server = UDPServer.new()
var port = 6969
var last_packet_time_ms = 0.0
var delay_smoothing_factor = 0.1
var smoothed_delay_ms = 0.0
signal delay_updated(new_delay)

var x_sensitivity = 25.0
var y_sensitivity = 25.0
var z_sensitivity = 2.0

# distance from ground
var z_offset = 18

# TODO where did we derive these values from ?
var fixed_rotation_target = Vector3(0, 2, 0)

var min_y_position = -20000.0
var max_y_position = 20000.0

var min_x_position = -20000.0
var max_x_position = 20000.0

var min_z_position = -20000.0
var max_z_position = 20000.0

var use_fixed_angle = true
var use_interpolation = true
# camera position interpolation smoothness parameter
var follow_speed = 20.0

func _ready():
	var result = udp_server.listen(port)
	if result != OK:
		print("failed to listen on port ", port)
		return
	print("listening on port ", port)
	
	var ui_node = get_node("/root/world/ui")
	if not ui_node:
		print("ui node not found, ensure path is correct")
		return
		
	ui_node.connect("main_camera_sensitivity_changed", func(value): 
		x_sensitivity = value
		y_sensitivity = value
	)
	
	ui_node.connect("main_camera_follow_speed_changed", func(value): 
		follow_speed = value
		print(follow_speed)
	)
	
	ui_node.connect("fov_changed", func(value): 
		fov = value
	)

# TODO _physics_process vs _process ?
func _physics_process(delta):
	# TODO do we even need this ?
	udp_server.poll()

	# TODO what does this do ?
	if not udp_server.is_connection_available():
		return
		
	var data = udp_server.take_connection().get_packet().get_string_from_utf8().split(" ")
	
	if not data.size() == 3:
		print("unexpected received data format, check parsing logic")
		return
		
	var current_time_ms = Time.get_ticks_msec()
	if last_packet_time_ms > 0:
		var current_delay_ms = current_time_ms - last_packet_time_ms
		# https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average
		smoothed_delay_ms = delay_smoothing_factor * current_delay_ms + (1.0 - delay_smoothing_factor) * smoothed_delay_ms
		emit_signal("delay_updated", smoothed_delay_ms)
		#print(int(smoothed_delay_ms), "ms")
	
	last_packet_time_ms = current_time_ms
		
	var received_x = clamp(float(data[0]), min_x_position, max_x_position)
	var received_y = clamp(float(data[1]), min_y_position, max_y_position)
	var received_z = clamp(float(data[2]), min_z_position, max_z_position)

	if Input.is_action_pressed("move_forward"):
		z_offset -= 0.5
	if Input.is_action_pressed("move_backward"):
		z_offset += 0.5

	var target_position = Vector3(
		-received_x * x_sensitivity,
		received_y * y_sensitivity,
		z_offset
	)
	
	if use_interpolation:
		# https://docs.godotengine.org/en/stable/tutorials/math/interpolation.html
		# https://en.wikipedia.org/wiki/Linear_interpolation
		global_position = global_position.lerp(target_position, delta * follow_speed)
	else:
		global_position = target_position

	if use_fixed_angle:
		look_at(fixed_rotation_target)
		
# free socket upon node deallocation
func _exit_tree():
	udp_server.stop()
