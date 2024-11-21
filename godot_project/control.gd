# ui file
extends Control

@export var Main: Camera3D
@export var Secondary: Camera3D

@onready var switch_camera_button = $GridContainer/Button
@onready var webcam_button = $GridContainer/Button2
@onready var toggle_fixed = $GridContainer/Button3
@onready var webcam = $GridContainer/Webcam
var current_camera: Camera3D
var camera_feed

func _ready():
	# Set the initial camera
	current_camera = Main
	current_camera.make_current()
	
	# Connect the button press to the switch_camera function
	switch_camera_button.pressed.connect(switch_camera)
	webcam_button.pressed.connect(webcam_visible)
	toggle_fixed.pressed.connect(toggle_fixed_setter)
	# Get the first camera feed
	var feeds = CameraServer.feeds()
	if feeds.size() > 0:
		camera_feed = feeds[0]
		camera_feed.set_active(true)

func webcam_visible():
	if !webcam.is_visible():
		webcam.show()

	else:
		webcam.hide()

func switch_camera():
	if current_camera == Main:
		Secondary.make_current()
		current_camera = Secondary
	else:
		Main.make_current()
		current_camera = Main
func toggle_fixed_setter():
	Main.look_at_fixed = !Main.look_at_fixed
	print("look_at_fixed is now: ", Main.look_at_fixed)
