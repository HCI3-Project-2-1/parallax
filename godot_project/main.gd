extends Node3D

func _ready():
	# Create a floor
	var floor = MeshInstance3D.new()
	var plane_mesh = PlaneMesh.new()
	plane_mesh.size = Vector2(10, 10)
	floor.mesh = plane_mesh
	floor.set_surface_override_material(0, StandardMaterial3D.new())
	add_child(floor)

	# Create a cube
	var cube = MeshInstance3D.new()
	cube.mesh = BoxMesh.new()
	cube.position = Vector3(0, 0.5, -3)
	add_child(cube)

	# Set up camera
	var camera = Camera3D.new()
	camera.position = Vector3(0, 2, 5)
	camera.look_at(Vector3.ZERO)
	add_child(camera)

	# Add light
	var light = DirectionalLight3D.new()
	light.position = Vector3(5, 5, 5)
	light.look_at(Vector3.ZERO)
	add_child(light)
