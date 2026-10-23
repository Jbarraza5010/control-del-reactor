extends Control

@onready var boton_ir_login: Button =  $CenterContainer/VBoxContainer/HBoxContainer/login
@onready var boton_ir_registro: Button = $CenterContainer/VBoxContainer/HBoxContainer/registro
@onready var boton_quit: Button = $CenterContainer/VBoxContainer/quit

func _ready() -> void:
	boton_ir_login.pressed.connect(func(): Navegacion.ir_a("auth/login"))
	boton_ir_registro.pressed.connect(func(): Navegacion.ir_a("auth/registro"))
	boton_quit.pressed.connect(func(): get_tree().quit())
