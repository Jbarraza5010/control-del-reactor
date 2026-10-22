extends Control

@onready var campo_correo: LineEdit = $CenterContainer/VBoxContainer/CampoCorreo
@onready var campo_clave: LineEdit = $CenterContainer/VBoxContainer/CampoClave
@onready var boton_ir_recuperacion: Button = $CenterContainer/VBoxContainer/BotonIrRecuperacion
@onready var boton_volver: Button = $CenterContainer/VBoxContainer/HBoxContainer/BotonVolver
@onready var boton_login: Button = $CenterContainer/VBoxContainer/HBoxContainer/BotonLogin
@onready var boton_ir_registro: Button = $CenterContainer/VBoxContainer/BotonIrRegistro
@onready var mensaje: Label = $CenterContainer/VBoxContainer/Mensaje

var MOCKING := true

func _ready() -> void:
	boton_ir_recuperacion.pressed.connect(func(): Navegacion.ir_a("auth/recuperacion"))
	boton_volver.pressed.connect(func(): Navegacion.ir_a("entrada"))
	boton_login.pressed.connect(_al_iniciar_sesion)
	boton_ir_registro.pressed.connect(func(): Navegacion.ir_a("auth/registro"))
	
func _al_iniciar_sesion() -> void:
	if MOCKING:
		# Asuma las credenciales:
		# correo: test@testing.com
		# contraseña: 12345678
		if campo_correo.text == "test@testing.com" and  campo_clave.text == "12345678":
			mensaje.text = "Inicio de sesión exitoso. Redirigiendo"
			await get_tree().create_timer(0.5).timeout
			Navegacion.ir_a("mainmenu")
		else:
			mensaje.text = "Correo o contraseña incorrecta. Intente otra vez"
			
		
