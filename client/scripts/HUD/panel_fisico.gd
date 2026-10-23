extends Node2D

@onready var boton_volver: Button = $CanvasLayer/HBoxContainer/BotonVolver
@onready var boton_detectar: Button = $CanvasLayer/HBoxContainer/BotonDetectar

func _ready() -> void:
	boton_volver.pressed.connect(func(): Navegacion.ir_a("mainmenu"))
	boton_detectar.pressed.connect(_detectar_panel_fisico)
	
func _detectar_panel_fisico() -> void:
	pass
