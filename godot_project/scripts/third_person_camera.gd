extends Camera3D

@export var main_camera : Camera3D

var move_speed = 1.0
var move_direction = Vector3()
var distance_behind_main_camera = 5.0

func _ready():
	var ui_node = get_node("/root/world/ui")
	if not ui_node:
		print("ui node not found, ensure path is correct")
		return
	
	ui_node.connect("third_person_camera_sensitivity_changed", func(value): move_speed = value)
	main_camera = get_node("/root/world/main_camera")
	if not main_camera:
		print("main_camera node not found, ensure path is correct")
		return

func _process(_delta):
	if Input.is_action_pressed("move_forward"):
		distance_behind_main_camera -= 0.25
	if Input.is_action_pressed("move_backward"):
		distance_behind_main_camera += 0.25
	
	translate(move_direction)

	var direction_to_look = main_camera.global_transform.basis.z.normalized()
	var behind_position = main_camera.global_transform.origin + direction_to_look * distance_behind_main_camera 
	global_transform.origin = behind_position
