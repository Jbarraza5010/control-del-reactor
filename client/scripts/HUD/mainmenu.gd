extends Control

@onready var boton_jugar: Button = $CenterContainer/VBoxContainer/BotonJugar
@onready var boton_panel: Button = $CenterContainer/VBoxContainer/BotonPanel
@onready var boton_quit: Button = $CenterContainer/VBoxContainer/BotonQuit
@onready var boton_perfil: Button = $BotonPerfil

func _ready() -> void:
	boton_panel.pressed.connect(func(): Navegacion.ir_a("hardware/panel_fisico"))
	boton_perfil.pressed.connect(func(): Navegacion.ir_a("profile/perfil"))
	boton_quit.pressed.connect(func(): get_tree().quit())
