extends Control

@export var Main: Camera3D
@export var Secondary: Camera3D

@onready var switch_camera_button = $Button
@onready var webcam_button = $Button2

var current_camera: Camera3D
var camera_feed

func _ready():
	# Set the initial camera
	current_camera = Main
	current_camera.make_current()
	
	# Connect the button press to the switch_camera function
	switch_camera_button.pressed.connect(switch_camera)
	webcam_button.pressed.connect(webcam_visible)
	# Get the first camera feed
	var feeds = CameraServer.feeds()
	print(feeds)
	if feeds.size() > 0:
		camera_feed = feeds[0]
		camera_feed.set_active(true)
		
func webcam_visible():
	if $Webcam.is_visible():
		$Webcam.hide()
	else:
		$Webcam.show()
func switch_camera():
	if current_camera == Main:
		Secondary.make_current()
		current_camera = Secondary
	else:
		Main.make_current()
		current_camera = Main
