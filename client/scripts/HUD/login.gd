extends Control

@onready var campo_correo: LineEdit = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/CampoCorreo
@onready var campo_contrasena: LineEdit = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/CampoContrasena
@onready var boton_ir_recuperacion: Button = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/BotonIrRecuperacion
@onready var boton_volver: Button = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/HBoxContainer/BotonVolver
@onready var boton_login: Button = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/HBoxContainer/BotonLogin
@onready var boton_ir_registro: Button = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/BotonIrRegistro
@onready var label_mensaje: Label = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/LabelMensaje

var MOCKING := true

func _ready() -> void:
	boton_ir_recuperacion.pressed.connect(func(): Navegacion.ir_a("auth/recuperacion"))
	boton_volver.pressed.connect(func(): Navegacion.ir_a("entrada"))
	boton_login.pressed.connect(_al_iniciar_sesion)
	boton_ir_registro.pressed.connect(func(): Navegacion.ir_a("auth/registro"))
	
func _al_iniciar_sesion() -> void:
	# Validaciones de campos no vacíos
	var correo := campo_correo.text.strip_edges()
	var contrasena := campo_contrasena.text
	
	if ValidacionCuenta.validar_login(correo, contrasena) != "":
		label_mensaje.text = ValidacionCuenta.validar_login(correo, contrasena)
	
	
	
	if MOCKING:
		# Asuma las credenciales:
		# correo: test@testing.com
		# contraseña: 12345678
		if correo == "test@testing.com" and  contrasena == "12345678":
			label_mensaje.text = "Inicio de sesión exitoso. Redirigiendo"
			await get_tree().create_timer(0.5).timeout
			Navegacion.ir_a("mainmenu")
		else:
			label_mensaje.text = "Correo o contraseña incorrecta. Intente otra vez"
			
		
