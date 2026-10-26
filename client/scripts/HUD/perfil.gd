extends Control

@onready var boton_volver : Button = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/BotonVolver

func _ready() -> void:
	boton_volver.pressed.connect(func(): Navegacion.ir_a("mainmenu"))
