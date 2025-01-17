extends StaticBody3D

var udp_server = UDPServer.new()
var port = 6969
var last_packet_time_ms = 0.0
var delay_smoothing_factor = 0.1
var smoothed_delay_ms = 0.0
signal delay_updated(new_delay)

# Tilt sensitivity (in radians)
var x_tilt_sensitivity = 1
var z_tilt_sensitivity = 1

# Maximum tilt angles (in radians)
var max_tilt_angle = PI/4  # 45 degrees

func _ready():
	var result = udp_server.listen(port)
	if result != OK:
		print("failed to listen on port ", port)
		return
	print("listening on port ", port)

func _physics_process(delta):
	udp_server.poll()

	if not udp_server.is_connection_available():
		return
		
	var data = udp_server.take_connection().get_packet().get_string_from_utf8().split(" ")
	
	if not data.size() == 3:
		print("unexpected received data format, check parsing logic")
		return
		
	var current_time_ms = Time.get_ticks_msec()
	if last_packet_time_ms > 0:
		var current_delay_ms = current_time_ms - last_packet_time_ms
		smoothed_delay_ms = delay_smoothing_factor * current_delay_ms + (1.0 - delay_smoothing_factor) * smoothed_delay_ms
		emit_signal("delay_updated", smoothed_delay_ms)
	
	last_packet_time_ms = current_time_ms
		
	var received_x = -float(data[0])
	var received_y = float(data[1])

	# Convert received coordinates to rotation angles
	var x_rotation = -received_y * x_tilt_sensitivity
	var z_rotation = -received_x * z_tilt_sensitivity
	
	# Apply rotation
	rotation.x = x_rotation
	rotation.z = z_rotation

func _exit_tree():
	udp_server.stop()
