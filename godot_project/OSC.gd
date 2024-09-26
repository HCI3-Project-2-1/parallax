extends Camera3D  # Or any other node you wish to control

# Declare OSC client
var osc_client = OSCSimple.new()
var face_position = Vector2.ZERO
var smoothing = 0.9  # Adjust the smoothing factor to control how smooth the transitions are

func _ready():
	# Bind the OSC client to port 8000
	var err = osc_client.bind(8000)
	if err != OK:
		print("Failed to bind OSC client on port 8000")
	else:
		print("OSC client bound to port 8000")
	osc_client.connect("osc_message_received", self, "_on_osc_message")

func _process(delta):
	# Poll for incoming OSC messages in each frame
	osc_client.poll()

func _on_osc_message(path, args):
	# Listen for OSC messages with path "/face"
	if path == "/face" and args.size() == 2:
		# Receive the normalized face position from OSC and apply smoothing
		var new_position = Vector2(float(args[0]), float(args[1]))
		face_position = face_position.lerp(new_position, smoothing)
		
		# Adjust the camera or node's position based on the face position
		var offset = Vector3(face_position.x, face_position.y, 0) * 0.1
		transform.origin = Vector3.ZERO + offset
		print("Camera position: ", transform.origin)  # Optional: Print to console for debugging

func _exit_tree():
	# Clean up the OSC client when the node is removed
	osc_client.unbind()
