extends Control

@export var main_camera: Camera3D
@export var third_person_camera: Camera3D

@export var delay_label :Label

@export var third_person_view_toggle :CheckButton
@export var fixed_angle_toggle  :CheckButton
@export var interpolation_toggle  :CheckButton
@export var settings_visibility_toggle : CheckButton
@export var settings_container : BoxContainer
@export var settings_panel : BoxContainer
@export var menu_button : MenuButton
@export var guide_button : Button
@export var guide_panel : Panel
@export var guide_container : VBoxContainer
@export var guide_text : Label
@export var opaque_panel : Panel

@export var main_camera_sensitivity_slider :HSlider
signal main_camera_sensitivity_changed(value)

@export var main_camera_follow_speed_slider :HSlider
signal main_camera_follow_speed_changed(value)

var camera_feed

func update_delay_label(new_delay):
	delay_label.text = "delay: " + str(int(new_delay)) + "ms"

func _ready():
	main_camera.make_current()

	main_camera_sensitivity_slider.connect("value_changed", func(value): emit_signal("main_camera_sensitivity_changed", value))
	main_camera_follow_speed_slider.connect("value_changed", func(value): emit_signal("main_camera_follow_speed_changed", value))
	

	
	third_person_view_toggle.pressed.connect(func(): third_person_camera.make_current() if main_camera == get_viewport().get_camera_3d() else main_camera.make_current())
	
	fixed_angle_toggle.pressed.connect(func(): main_camera.use_fixed_angle = not main_camera.use_fixed_angle)
	
	interpolation_toggle.pressed.connect(func(): main_camera.use_interpolation = not main_camera.use_interpolation)
	
	settings_visibility_toggle.pressed.connect(func(): settings_container.visible = not settings_container.visible)
	settings_visibility_toggle.pressed.connect(func(): opaque_panel.visible = not opaque_panel.visible)
	settings_visibility_toggle.pressed.connect(func(): delay_label.visible = not delay_label.visible)
	settings_visibility_toggle.pressed.connect(func(): menu_button.visible = not menu_button.visible)
	settings_visibility_toggle.pressed.connect(func(): guide_button.visible = not guide_button.visible)
	guide_button.pressed.connect(func(): guide_panel.visible = not guide_panel.visible)
	guide_button.pressed.connect(func(): guide_text.visible = not guide_text.visible)
