extends Camera3D

var udp_server = UDPServer.new()
var port = 12345

var face_position = Vector2.ZERO
var smoothing = 0.9
var sensitivity = 20.0  # Increase this value to amplify head movement effects

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
			print("Received data: ", data)  # Debug print
			var new_position = Vector2(float(data[0]), float(data[1]))
			face_position = face_position.lerp(new_position, smoothing)
	
	# Adjusted sensitivity for rotation
	var rotation_x = face_position.y * -PI / 4 * sensitivity  # Increase up-down rotation (pitch)
	var rotation_y = face_position.x * PI / 4 * sensitivity   # Increase left-right rotation (yaw)
	
	rotation_degrees.x = lerp_angle(rotation_degrees.x, rotation_x, smoothing)  # Smooth pitch rotation
	rotation_degrees.y = lerp_angle(rotation_degrees.y, rotation_y, smoothing)  # Smooth yaw rotation
	
	print("Camera rotation: ", rotation_degrees)  # Debug print

func _exit_tree():
	udp_server.stop()
