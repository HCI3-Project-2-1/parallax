extends Control

@export var menu : MenuButton

func _ready():
	var popup = menu.get_popup()
	popup.add_item("Boxes")
	popup.add_item("Tunnel")
	popup.add_item("Balance")
	popup.id_pressed.connect(_on_menu_item_pressed)

func _on_menu_item_pressed(id: int):
	var scene_path = ""
	
	match id:
		0: # Boxes
			scene_path = "res://scenes/main.tscn"
		1: # Tunnel
			scene_path = "res://scenes/tunnel.tscn"
		2: # Balance
			scene_path = "res://scenes/balance.tscn"
	
	if scene_path != "":
		SceneManager.change_scene(
			scene_path,
			{ 
				"pattern": "scribbles", 
				"pattern_leave": "scribbles" 
			}
		)
