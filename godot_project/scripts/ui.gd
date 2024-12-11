extends Control

@export var main_camera: Camera3D
@export var third_person_camera: Camera3D

@onready var delay_label = $delay_label

@onready var third_person_view_toggle = $third_person_view_toggle
@onready var camera_output_toggle = $camera_output_toggle
@onready var fixed_angle_toggle = $fixed_angle_toggle
@onready var interpolation_toggle = $interpolation_toggle

@onready var main_camera_sensitivity_slider = $main_camera_sensitivity_slider
signal main_camera_sensitivity_changed(value)

@onready var main_camera_follow_speed_slider = $main_camera_follow_speed_slider
signal main_camera_follow_speed_changed(value)



@onready var third_person_camera_sensitivity_slider = $third_person_camera_sensitivity_slider
signal third_person_camera_sensitivity_changed(value)

var camera_feed

func update_delay_label(new_delay):
	delay_label.text = "delay: " + str(int(new_delay)) + "ms"

func _ready():
	main_camera.make_current()

	main_camera_sensitivity_slider.connect("value_changed", func(value): emit_signal("main_camera_sensitivity_changed", value))
	main_camera_follow_speed_slider.connect("value_changed", func(value): emit_signal("main_camera_follow_speed_changed", value))
	
	third_person_camera_sensitivity_slider.connect("value_changed", func(value): emit_signal("third_person_camera_sensitivity_changed", value))
	
	third_person_view_toggle.pressed.connect(func(): third_person_camera.make_current() if main_camera == get_viewport().get_camera_3d() else main_camera.make_current())
	fixed_angle_toggle.pressed.connect(func(): main_camera.use_fixed_angle = not main_camera.use_fixed_angle)
	interpolation_toggle.pressed.connect(func(): main_camera.use_interpolation = not main_camera.use_interpolation)
