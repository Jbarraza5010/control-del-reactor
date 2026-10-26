extends Control

@onready var campo_correo: LineEdit = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/HBoxContainer/CampoCorreo
@onready var boton_enviar_codigo: Button = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/HBoxContainer/BotonEnviarCodigo
@onready var campo_codigo: LineEdit = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/CampoCodigo
@onready var campo_contrasena: LineEdit = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/CampoContrasena
@onready var boton_volver: Button = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/HBoxContainer2/BotonVolver
@onready var boton_validar: Button = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/HBoxContainer2/BotonValidar
@onready var label_mensaje: Label = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/LabelMensaje

func _ready() -> void:
	boton_volver.pressed.connect(func(): Navegacion.ir_a("auth/login"))
	boton_enviar_codigo.pressed.connect(_enviar_codigo)
	boton_validar.pressed.connect(_enviar_clave_al_correo)

func _enviar_codigo() -> void:
	var correo: String = campo_correo.text.strip_edges()
	var err_correo: String = ValidacionCuenta.validar_correo(correo)
	if err_correo != "":
		label_mensaje.text = err_correo
		return

	boton_enviar_codigo.disabled = true
	var response: Dictionary = await Api.post_json("/api/v1/auth/forgot-password", {
		"email": correo,
	})
	boton_enviar_codigo.disabled = false

	if response.get("ok", false):
		label_mensaje.text = "Se ha enviado un código de un solo uso al correo %s" % correo
	else:
		label_mensaje.text = Api.mensaje_error(response, "No se pudo enviar el código de recuperación.")

func _enviar_clave_al_correo() -> void:
	var correo: String = campo_correo.text.strip_edges()
	var codigo: String = campo_codigo.text.strip_edges()
	var nueva_contrasena: String = campo_contrasena.text

	if correo != "":
		var err_correo: String = ValidacionCuenta.validar_correo(correo)
		if err_correo != "":
			label_mensaje.text = err_correo
			return

	var err_codigo: String = ValidacionCuenta.validar_codigo(codigo)
	if err_codigo != "":
		label_mensaje.text = err_codigo
		return

	var err_contrasena: String = ValidacionCuenta.validar_contrasena(nueva_contrasena)
	if err_contrasena != "":
		label_mensaje.text = err_contrasena
		return

	var payload: Dictionary = {
		"code": codigo,
		"new_password": nueva_contrasena,
	}
	if correo != "":
		payload["email"] = correo

	boton_validar.disabled = true
	var response: Dictionary = await Api.post_json("/api/v1/auth/reset-password", payload)
	boton_validar.disabled = false

	if response.get("ok", false):
		label_mensaje.text = "Contraseña actualizada exitosamente. Redirigiendo..."
		await get_tree().create_timer(0.5).timeout
		Navegacion.ir_a("auth/login")
	else:
		label_mensaje.text = Api.mensaje_error(response, "No se ha podido restablecer la contraseña. Intente otra vez")
