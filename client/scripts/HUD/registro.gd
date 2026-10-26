extends Control

@onready var campo_usuario: LineEdit = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/CampoUsuario
@onready var campo_correo: LineEdit = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/CampoCorreo
@onready var campo_contrasena: LineEdit = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/CampoContrasena
@onready var boton_registrar: Button = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/HBoxContainer/BotonRegistrar
@onready var boton_volver: Button = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/HBoxContainer/BotonVolver
@onready var boton_ir_login: Button = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/BotonIrLogin
@onready var label_mensaje: Label = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/LabelMensaje

func _ready() -> void:
	boton_registrar.pressed.connect(_al_registrar)
	boton_ir_login.pressed.connect(func(): Navegacion.ir_a("auth/login"))
	boton_volver.pressed.connect(func(): Navegacion.ir_a("entrada"))

func _al_registrar() -> void:
	# Validaciones del frontend
	var usuario: String = campo_usuario.text.strip_edges()
	var correo: String = campo_correo.text.strip_edges()
	var contrasena: String = campo_contrasena.text

	# Validar nombre de usuario
	var err_usuario: String = ValidacionCuenta.validar_usuario(usuario)
	if err_usuario != "":
		label_mensaje.text = err_usuario
		return
	# Validar correo electronico
	var err_correo: String = ValidacionCuenta.validar_correo(correo)
	if err_correo != "":
		label_mensaje.text = err_correo
		return
	# Validar contrasena
	var err_contrasena: String = ValidacionCuenta.validar_contrasena(contrasena)
	if err_contrasena != "":
		label_mensaje.text = err_contrasena
		return

	# Envío de datos al backend
	boton_registrar.disabled = true
	var response: Dictionary = await Api.post_json("/api/v1/auth/register", {
		"username": usuario,
		"email": correo,
		"password": contrasena,
	})
	boton_registrar.disabled = false

	if response.get("ok", false):
		Api.correo_pendiente = correo
		Navegacion.ir_a("auth/verificacion")
	else:
		label_mensaje.text = Api.mensaje_error(response, "Ocurrió un error al registrar la cuenta.")
