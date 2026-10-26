extends Node

func ir_a(nombre_escena: String) -> void:
	get_tree().change_scene_to_file("res://scenes/%s.tscn" % nombre_escena)
