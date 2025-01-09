extends Control

var main_scene := preload("res://scenes/main.tscn")
var running_mode := MediaPipeTask.RUNNING_MODE_IMAGE
var delegate := MediaPipeTaskBaseOptions.DELEGATE_CPU
var camera_helper := MediaPipeCameraHelper.new()
var camera_resolution = Vector2(640, 480)

@onready var camera_node: Camera3D = $"../main_camera"
@onready var camera_view: TextureRect = $camera_view
@onready var video_player: VideoStreamPlayer = $video_stream_player
@onready var load_video_button: Button = $load_video_button
@onready var open_camera_button: Button = $open_camera_button
@onready var video_file_dialog: FileDialog = $video_file_dialog
@onready var permission_dialog: AcceptDialog = $camera_permission_dialog

var task: MediaPipeFaceLandmarker
var task_file := "res://assets/face_landmarker.task"
var LANDMARK_IDX = 1

# for live video processing
func _result_callback(result: MediaPipeFaceLandmarkerResult, image: MediaPipeImage, timestamp_ms: int) -> void:
	if result.face_landmarks.is_empty():
		return
	# nose tip from first detected face
	var nose_tip = result.face_landmarks[0].landmarks[LANDMARK_IDX]
	var final_image = image.get_image()
	camera_node.call_deferred("update_position", transform_landmark_coords(Vector3(nose_tip.x, nose_tip.y, nose_tip.z), Vector2(final_image.get_width(), final_image.get_height()), camera_node))
	draw_mark_point(final_image, nose_tip)
	update_camera_view(final_image)


func init_task() -> void:
	var base_options := MediaPipeTaskBaseOptions.new()
	base_options.delegate = delegate
	var file := FileAccess.open(task_file, FileAccess.READ)
	base_options.model_asset_buffer = file.get_buffer(file.get_length())
	task = MediaPipeFaceLandmarker.new()
	task.initialize(base_options, running_mode, 1, 0.5, 0.5, 0.5, true)
	task.result_callback.connect(self._result_callback)

func process_video_frame(image: Image, timestamp_ms: int) -> void:
	var input_image := MediaPipeImage.new()
	input_image.set_image(image)
	var start_time = Time.get_ticks_msec()
	var result := task.detect_video(input_image, timestamp_ms)
	var end_time = Time.get_ticks_msec() - start_time
	print("took ", end_time, "ms")
	var nose_tip = result.face_landmarks[0].landmarks[LANDMARK_IDX]
	camera_node.update_position(Vector3(nose_tip.x, nose_tip.y, nose_tip.z))
	draw_mark_point(image, nose_tip)
	update_camera_view(image)

func process_camera_frame(image: MediaPipeImage, timestamp_ms: int) -> void:
	task.detect_async(image, timestamp_ms)

func transform_landmark_coords(landmark: Vector3, image_size: Vector2, camera: Camera3D) -> Vector3:
	var pixel_x = landmark.x * image_size.x
	var pixel_y = landmark.y * image_size.y
	
	# transform from image coordinate system (top-left origin) 
	# to screen coordinate system (center origin)
	var ndc_x = (pixel_x / image_size.x) * 2.0 - 1.0
	var ndc_y = -((pixel_y / image_size.y) * 2.0 - 1.0)
	var min_depth = 0.5
	var max_depth = 5.0
	var depth = lerp(min_depth, max_depth, landmark.z)
	
	return Vector3(ndc_x, ndc_y, depth)

func draw_mark_point(image: Image, landmark: MediaPipeNormalizedLandmark) -> void:
	var color := Color.GREEN
	var rect := Image.create(8, 8, false, image.get_format())
	rect.fill(color)

	var pos := Vector2(landmark.x, landmark.y)
	image.blit_rect(rect, rect.get_used_rect(), Vector2i(Vector2(image.get_size()) * pos) - rect.get_size() / 2)

func _ready():
	load_video_button.pressed.connect(self._open_video)
	open_camera_button.pressed.connect(self._open_camera)
	
	video_file_dialog.file_selected.connect(self._load_video)
	
	camera_helper.permission_result.connect(self._permission_result)
	camera_helper.new_frame.connect(self._camera_frame)
	init_task()

func _process(delta: float) -> void:
	if not video_player:
		return
	
	if video_player.is_playing():
		var texture := video_player.get_video_texture()
		if texture:
			var image := texture.get_image()
			if image:
				if not running_mode == MediaPipeTask.RUNNINE_MODE_VIDEO:
					running_mode = MediaPipeTask.RUNNINE_MODE_VIDEO
					init_task()
				process_video_frame(image, Time.get_ticks_msec())

func _back() -> void:
	reset()
	get_tree().change_scene_to_packed(main_scene)

func _open_video() -> void:
	video_file_dialog.popup_centered_ratio()

func _load_video(path: String) -> void:
	reset()
	var stream: VideoStream = load(path)
	video_player.stream = stream
	video_player.play()

func _open_camera() -> void:
	if camera_helper.permission_granted():
		start_camera()
	else:
		camera_helper.request_permission()

func _permission_result(granted: bool) -> void:
	if granted:
		start_camera()
	else:
		permission_dialog.popup_centered()

func _camera_frame(image: MediaPipeImage) -> void:
	if not running_mode == MediaPipeTask.RUNNING_MODE_LIVE_STREAM:
		running_mode = MediaPipeTask.RUNNING_MODE_LIVE_STREAM
		init_task()
	if delegate == MediaPipeTaskBaseOptions.DELEGATE_CPU and image.is_gpu_image():
		image.convert_to_cpu()
	process_camera_frame(image, Time.get_ticks_msec())

func update_camera_view(image: Image) -> void:
	if Vector2i(camera_view.texture.get_size()) == image.get_size():
		camera_view.texture.call_deferred("update", image)
	else:
		camera_view.texture.call_deferred("set_image", image)

func start_camera() -> void:
	reset()
	camera_helper.set_mirrored(true)
	camera_helper.start(MediaPipeCameraHelper.FACING_FRONT, camera_resolution)

func reset() -> void:
	if video_player:
		video_player.stop()
	if camera_helper:
		camera_helper.close()
