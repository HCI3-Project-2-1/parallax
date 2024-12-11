extends Control

@export var ball: RigidBody3D
@export var platform: StaticBody3D
@export var respawn_button: Button
@export var sensitivity_slider: Slider
@export var weight_slider: Slider
@export var start_button: Button
@export var score_label: Label
@export var timer_label: Label

var initial_ball_position: Vector3
var initial_platform_scale: Vector3
var game_active = false
var score = 0.0
var elapsed_time = 0.0
var shrink_rate = 0.96
var score_rate = 10.0
var grace_period = 0.5
var time_off_platform = 0.0
var fall_threshold = 0.0

# Score styling variables
var base_font_size = 40
var color_threshold = 100  # Score at which colors start changing
var size_increment_step = 50  # Score interval for increasing font size
var color_change_speed = 2.0  # How fast colors change

func _ready():
	if !ball or !platform or !respawn_button:
		push_error("Required nodes not assigned in GameManager")
		return
		
	initial_ball_position = ball.global_position
	initial_platform_scale = platform.scale
	
	respawn_button.pressed.connect(_on_respawn_pressed)
	sensitivity_slider.value_changed.connect(_on_sensitivity_changed)
	weight_slider.value_changed.connect(_on_weight_changed)
	start_button.pressed.connect(_on_start_pressed)
	start_button.text = "Start"
	
func _process(delta):
	if !game_active:
		return
		
	elapsed_time += delta
	timer_label.text = "Time: " + format_time(elapsed_time)
	
	if is_ball_on_platform():
		time_off_platform = 0.0
		score += score_rate * delta
		update_score_display(delta)
		
		# Shrink platform over time
		platform.scale *= pow(shrink_rate, delta)
	else:
		time_off_platform += delta
		if time_off_platform >= grace_period:
			_on_ball_fell()

func update_score_display(delta: float):
	if !score_label:
		return
		
	var score_text = "Score: " + str(int(score))
	
	# Update font size
	var size_multiplier = 1 + (floor(score / size_increment_step) * 0.2)  # Increase size by 20% every size_increment_step points
	score_label.add_theme_font_size_override("font_size", int(base_font_size * size_multiplier))
	
	# Update color if above threshold
	if score >= color_threshold:
		var hue = fmod(elapsed_time * color_change_speed, 1.0)
		var color = Color.from_hsv(hue, 1, 1)
		score_label.add_theme_color_override("font_color", color)
	else:
		score_label.remove_theme_color_override("font_color")
	
	score_label.text = score_text

func _on_start_pressed():
	start_button.text = "Restart"
	game_active = true
	score = 0
	elapsed_time = 0
	time_off_platform = 0
	platform.scale = initial_platform_scale
	_on_respawn_pressed()
	
	# Reset score label styling
	if score_label:
		score_label.remove_theme_color_override("font_color")
		score_label.add_theme_font_size_override("font_size", base_font_size)

func _on_ball_fell():
	score = 0
	elapsed_time = 0
	_on_respawn_pressed()
	
	# Reset score label styling
	if score_label:
		score_label.remove_theme_color_override("font_color")
		score_label.add_theme_font_size_override("font_size", base_font_size)
		score_label.text = "Score: 0"

func is_ball_on_platform() -> bool:
	return ball.global_position.y > fall_threshold

func format_time(seconds: float) -> String:
	var minutes = int(seconds / 60)
	var remaining_seconds = int(seconds) % 60
	return "%d:%02d" % [minutes, remaining_seconds]

func _on_respawn_pressed():
	if !ball or !platform:
		return
		
	ball.position = initial_ball_position
	ball.linear_velocity = Vector3.ZERO
	ball.angular_velocity = Vector3.ZERO
	platform.scale = initial_platform_scale

func _on_sensitivity_changed(value: float):
	if platform:
		platform.x_tilt_sensitivity = value
		platform.z_tilt_sensitivity = value

func _on_weight_changed(value: float):
	if ball:
		ball.mass = value
