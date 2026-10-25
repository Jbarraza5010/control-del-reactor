extends Control

@onready var boton_ir_login: Button =  $CenterContainer/VBoxContainer/HBoxContainer/BotonLogin
@onready var boton_ir_registro: Button = $CenterContainer/VBoxContainer/HBoxContainer/BotonRegistro
@onready var boton_quit: Button = $CenterContainer/VBoxContainer/BotonSalir

func _ready() -> void:
	boton_ir_login.pressed.connect(func(): Navegacion.ir_a("auth/login"))
	boton_ir_registro.pressed.connect(func(): Navegacion.ir_a("auth/registro"))
	boton_quit.pressed.connect(func(): get_tree().quit())
