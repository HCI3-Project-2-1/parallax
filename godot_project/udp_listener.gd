extends Node  # Using Node for UDP testing functionality

var udp_server = UDPServer.new()
var port = 13456  # Adjust the port if needed

var total_latency_sum = 0.0  # Sum of timestamp differences and processing times
var package_number = 0  # To track the total number of packets
var old_timestamp = -1.0  # Initialize with -1.0 to indicate no previous timestamp
var max_packages = 100  # Maximum packets to log; make it configurable.
						# This can be removed or changed based on the needs.
var log_data = []  # Store packet data in a list for structured output

# Store the start time in microseconds when the script begins
var start_time = 0  # To store the initial time when the script is run

# Called when the node enters the scene tree for the first time
func _ready():
	# Start the UDP server
	var err = udp_server.listen(port)
	if err != OK:
		print("Failed to listen on port ", port)
		return
	print("Listening on port ", port)
	
	# Capture the start time in microseconds
	start_time = Time.get_ticks_usec()
	
	# Add a way to stop the server manually (for example, after 10 seconds)
	# You can press the escape key to stop the server
	set_process_input(true)

# Called every frame
func _process(delta):
	udp_server.poll()

	if udp_server.is_connection_available() and package_number < max_packages:
		# Start measuring the time to process the data
		var processing_start = Time.get_ticks_usec()

		var peer = udp_server.take_connection()
		var packet = peer.get_packet()
		var data = packet.get_string_from_utf8().split(",")

		if data.size() == 4:  # Expecting timestamp, norm_x, norm_y, and norm_z
			# Extract data
			var raw_timestamp = float(data[0])  # First part is the timestamp from the UDP message (in seconds)
			var norm_x = float(data[1])         # Normalized X coordinate
			var norm_y = float(data[2])         # Normalized Y coordinate
			var norm_z = float(data[3])         # Normalized Z coordinate
			
			# Convert the raw timestamp to microseconds and adjust it to be relative to start_time
			var timestamp = int(raw_timestamp * 1_000_000) - start_time

			# Initialize timestamp_diff to 0 if it's the first packet
			var timestamp_diff = 0.0

			# If this is not the first packet, calculate the timestamp difference in microseconds
			if old_timestamp != -1.0:
				timestamp_diff = timestamp - old_timestamp  # Keep in microseconds

			# Update the old timestamp for the next packet
			old_timestamp = timestamp

			# End measuring the time to process the data
			var processing_end = Time.get_ticks_usec()
			var processing_time = (processing_end - processing_start) / 1_000_000.0  # Convert microseconds to seconds

			# Calculate total time for this packet in seconds (for average calculation)
			var total_time = timestamp_diff / 1_000_000.0 + processing_time  # Convert delay to seconds before adding
			total_latency_sum += total_time

			# Store data in log_data array for output after reaching max packages, with delay in microseconds
			log_data.append({"norm_x": norm_x, "norm_y": norm_y, "norm_z": norm_z, "delay": timestamp_diff})
			
			# Increment the package counter
			package_number += 1

# Function to calculate and print the average latency and log data after reaching max packages
func calculate_average_latency_and_output():
	if package_number > 0:
		var avg_latency = (total_latency_sum / package_number) * 1_000  # Convert average delay to milliseconds
		print("Final Average Delay (timestamp diff): %.2f milliseconds" % avg_latency)

		# Print header for log data
		print("X Coordinate | Y Coordinate | Z Coordinate | Delay (μs)")
		print("-------------------------------------------------------")
		
		# Print each row in log_data, with delay in microseconds
		for entry in log_data:
			print("%.4f       | %.4f       | %.4f       | %d" % [entry["norm_x"], entry["norm_y"], entry["norm_z"], entry["delay"]])

# Input function to handle key presses
func _input(event):
	if event.is_action_pressed("ui_cancel"):  # Example: pressing the escape key
		print("Stopping the UDP server and calculating average delay...")
		calculate_average_latency_and_output()
		udp_server.stop()
		get_tree().quit()  # Exit the application
