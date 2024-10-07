extends Node  # Using Node for UDP testing functionality

var udp_server = UDPServer.new()
var port = 13456  # Adjust the port if needed

var total_latency_sum = 0.0  # Sum of timestamp differences and processing times
var Package_Number = 0  # To track the total number of packets
var old_timestamp = -1.0  # Initialize with -1.0 to indicate no previous timestamp

# Called when the node enters the scene tree for the first time
func _ready():
	# Start the UDP server
	var err = udp_server.listen(port)
	if err != OK:
		print("Failed to listen on port ", port)
		return
	print("Listening on port ", port)
	
	# Add a way to stop the server manually (for example, after 10 seconds)
	# You can press the escape key to stop the server
	set_process_input(true)

# Called every frame
func _process(delta):
	udp_server.poll()

	if udp_server.is_connection_available():
		# Start measuring the time to process the data
		var processing_start = Time.get_ticks_usec()

		var peer = udp_server.take_connection()
		var packet = peer.get_packet()
		var data = packet.get_string_from_utf8().split(",")

		if data.size() == 3:  # Expecting timestamp, norm_x, and norm_y
			# Extract data
			var timestamp = float(data[0])  # First part is the timestamp from the UDP message
			var norm_x = float(data[1])     # Normalized X coordinate
			var norm_y = float(data[2])     # Normalized Y coordinate

			# Update the packet counter
			Package_Number += 1

			# Log current packet number and timestamp
			# print("Packet Number: ", Package_Number)

			# Initialize timestamp_diff to 0 if it's the first packet
			var timestamp_diff = 0.0

			# If this is not the first packet, calculate the timestamp difference
			if old_timestamp != -1.0:
				timestamp_diff = timestamp - old_timestamp
				# print("Timestamp difference: ", timestamp_diff, " seconds")

			# Update the old timestamp for the next packet
			old_timestamp = timestamp

			# End measuring the time to process the data
			var processing_end = Time.get_ticks_usec()
			var processing_time = (processing_end - processing_start) / 1000000.0  # Convert microseconds to seconds

			# Sum timestamp difference and processing time
			var total_time = timestamp_diff + processing_time
			total_latency_sum += total_time

			# print("Data processing time: ", processing_time, " seconds")
			# print("Total time for this packet (timestamp diff + processing): ", total_time, " seconds")

			# Log the received data
			# print("Received data - Norm X: ", norm_x, " Norm Y: ", norm_y)

# Function to calculate and print the average latency
func calculate_average_latency():
	if Package_Number > 0:
		var avg_latency = total_latency_sum / Package_Number
		var avg_latency_ms = avg_latency * 1000  # Convert seconds to milliseconds
		print("Final Average Latency (timestamp diff + processing): %.2f milliseconds" % avg_latency_ms)

# Input function to handle key presses
func _input(event):
	if event.is_action_pressed("ui_cancel"):  # Example: pressing the escape key
		print("Stopping the UDP server and calculating average latency...")
		calculate_average_latency()
		udp_server.stop()
		get_tree().quit()  # Exit the application
