extends Control

# Node References
@export var ball: RigidBody3D
@export var platform: StaticBody3D
@export var ground_detector: Area3D

# UI Elements
@export var start_button: Button
@export var stop_button: Button
@export var respawn_button: Button
@export var score_label: Label
@export var timer_label: Label
@export var opaque_panel : Panel
@export var menu_button : MenuButton
@export var guide_button : Button
@export var guide_panel : Panel
@export var guide_text : Label
@export var guide_container : VBoxContainer
@export var settings_visibility_toggle : CheckButton
@export var settings_container : BoxContainer
@export var settings_panel : BoxContainer
@export var score_time_container : GridContainer

# Control Elements
@export var sensitivity_slider: Slider
@export var shrink_slider: Slider
@export var sensitivity_label: Label
@export var shrink_label: Label

# Effects
@export var explosion_particles: GPUParticles3D
@export var sound_effect: AudioStreamPlayer3D

# Game State Variables
var game_active = false
var score = 0.0
var elapsed_time = 0.0
var initial_ball_position: Vector3
var initial_platform_scale: Vector3

# Game Parameters
var shrink_rate = 0.96
var score_rate = 10.0
var grace_period = 0.5
var fall_threshold = 2.5
var sensitivity = 0.0

# Score Styling Parameters
var base_font_size = 40
var color_threshold = 100  # Score at which colors start changing
var size_increment_step = 50  # Score interval for increasing font size
var color_change_speed = 2.0  # How fast colors change

# Initialize game components and connect signals
func _ready():
	if !_validate_required_nodes():
		return

	_setup_initial_values()
	_connect_signals()
	_deactivate_game()  # Ensure game is not active at the start.
	ball.freeze = true  # Freeze ball at the start.

# Main game loop
func _process(delta):
	if !game_active:
		return
	_update_game_state(delta)

# Validation and Setup Functions
func _validate_required_nodes() -> bool:
	if !ball or !platform or !respawn_button:
		push_error("Required nodes not assigned in GameManager")
		return false
	return true

func _setup_initial_values():
	initial_ball_position = ball.global_transform.origin
	initial_platform_scale = platform.scale
	shrink_label.text = "Shrink rate: " + str(shrink_rate)
	sensitivity_label.text = "Sensitivity: " + str(sensitivity)

func _connect_signals():
	ground_detector.body_entered.connect(_on_ground_collision)
	
	respawn_button.pressed.connect(_on_respawn_pressed)
	
	stop_button.pressed.connect(_on_stop_pressed)
	
	sensitivity_slider.value_changed.connect(_on_sensitivity_changed)
	
	shrink_slider.value_changed.connect(_on_shrink_rate_changed)
	
	start_button.pressed.connect(_on_start_pressed)
	
	settings_visibility_toggle.pressed.connect(func(): settings_container.visible = not settings_container.visible)
	settings_visibility_toggle.pressed.connect(func(): menu_button.visible = not menu_button.visible)
	settings_visibility_toggle.pressed.connect(func(): opaque_panel.visible = not opaque_panel.visible)
	settings_visibility_toggle.pressed.connect(func(): score_label.visible = not score_label.visible)
	settings_visibility_toggle.pressed.connect(func(): timer_label.visible = not timer_label.visible)
	settings_visibility_toggle.pressed.connect(func(): guide_button.visible = not guide_button.visible)
	guide_button.pressed.connect(func(): guide_panel.visible = not guide_panel.visible)
	guide_button.pressed.connect(func(): guide_text.visible = not guide_text.visible)

# Game State Update Functions
func _update_game_state(delta):
	elapsed_time += delta
	timer_label.text = "Time: " + format_time(elapsed_time)

	if is_ball_on_platform():
		_handle_active_gameplay(delta)
	else:
		_on_ball_fell()

func _handle_active_gameplay(delta):
	score += (score_rate * delta)
	update_score_display(delta)
	platform.scale *= pow(shrink_rate, delta)

# Visual Effects Functions
func trigger_explosion():
	if explosion_particles:
		explosion_particles.global_position = ball.global_position
		explosion_particles.restart()
		explosion_particles.emitting = true
		ball.visible = false

func update_score_display(delta: float):
	if !score_label:
		return

	var score_text = "Score: " + str(int(score))
	_update_score_styling(delta)
	score_label.text = score_text

func _update_score_styling(delta: float):
	# Update font size based on score
	var size_multiplier = 1 + (floor(score / size_increment_step) * 0.2)
	score_label.add_theme_font_size_override("font_size", int(base_font_size * size_multiplier))

	# Update color if above threshold
	if score >= color_threshold:
		var hue = fmod(elapsed_time * color_change_speed, 1.0)
		score_label.add_theme_color_override("font_color", Color.from_hsv(hue, 1, 1))
	else:
		score_label.remove_theme_color_override("font_color")

# Event Handlers
func _on_start_pressed():
	ball.freeze = false
	stop_button.text = "Stop"
	start_button.text = "Restart"
	ball
	_on_respawn_pressed()
	_activate_game()  

func _on_stop_pressed():
	if ball.freeze == false:
		ball.freeze = true
		game_active = false
		stop_button.text = "Continue"
	else:
		ball.freeze = false 
		game_active = true
		stop_button.text = "Stop"





func _on_ball_fell():
	_deactivate_game()

func _on_ground_collision(body: Node3D):
	if body == ball:
		sound_effect.playing = true
		trigger_explosion()
		_on_ball_fell()

# Utility Functions
func _activate_game():
	game_active = true
	score = 0
	elapsed_time = 0
	platform.scale = initial_platform_scale
	ball.visible = true 
	ball.sleeping = false  
  

	# Reset score label
	if score_label:
		score_label.remove_theme_color_override("font_color")
		score_label.add_theme_font_size_override("font_size", base_font_size)

	# Clear the waiting message (optional)
	if timer_label:
		timer_label.text = ""

func _deactivate_game():
	game_active = false
	ball.freeze = true  
  

	# Show a waiting message (optional)
	if timer_label:
		timer_label.text = "Press Start to Begin"


func is_ball_on_platform() -> bool:
	return ball.global_position.y > fall_threshold

func format_time(seconds: float) -> String:
	var minutes = int(seconds / 60)
	var remaining_seconds = int(seconds) % 60
	return "%d:%02d" % [minutes, remaining_seconds]

# Control Value Changes
func _on_sensitivity_changed(value: float):
	if platform:
		platform.x_tilt_sensitivity = value
		platform.z_tilt_sensitivity = value
		sensitivity_label.text = "Sensitivity: " + str(value)

func _on_shrink_rate_changed(value: float):
	shrink_label.text = "Shrink rate: " + str(value)
	shrink_rate = value

func _on_respawn_pressed():
	if !ball or !platform:
		print("Respawn failed: Missing ball or platform reference.")
		return

	# Reset ball position and velocities
	ball.global_transform.origin = initial_ball_position
	ball.linear_velocity = Vector3.ZERO
	ball.angular_velocity = Vector3.ZERO
	ball.sleeping = false
	ball.visible = true

	# Reset platform scale
	platform.scale = initial_platform_scale
