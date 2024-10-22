extends Camera3D

@export var Main : Camera3D
# Speed of the camera movement
var move_speed = 8.0  # Speed at which the camera moves

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	#look_at(Main.global_position, Vector3.UP)
	# Handle movement input (WASD)
	_handle_movement(delta)

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
