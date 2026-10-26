extends Control

@onready var campo_correo: LineEdit = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/CampoCorreo
@onready var campo_contrasena: LineEdit = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/CampoContrasena
@onready var boton_ir_recuperacion: Button = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/BotonIrRecuperacion
@onready var boton_volver: Button = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/HBoxContainer/BotonVolver
@onready var boton_login: Button = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/HBoxContainer/BotonLogin
@onready var boton_ir_registro: Button = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/BotonIrRegistro
@onready var label_mensaje: Label = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/LabelMensaje

func _ready() -> void:
	boton_ir_recuperacion.pressed.connect(func(): Navegacion.ir_a("auth/recuperacion"))
	boton_volver.pressed.connect(func(): Navegacion.ir_a("entrada"))
	boton_login.pressed.connect(_al_iniciar_sesion)
	boton_ir_registro.pressed.connect(func(): Navegacion.ir_a("auth/registro"))

func _al_iniciar_sesion() -> void:
	var correo: String = campo_correo.text.strip_edges()
	var contrasena: String = campo_contrasena.text

	var err_login: String = ValidacionCuenta.validar_login(correo, contrasena)
	if err_login != "":
		label_mensaje.text = err_login
		return

	boton_login.disabled = true
	var response: Dictionary = await Api.post_json("/api/v1/auth/login", {
		"email": correo,
		"password": contrasena,
	})
	boton_login.disabled = false

	if response.get("ok", false):
		var data: Dictionary = response.get("data", {})
		Api.token = str(data.get("token", ""))
		var user_data: Variant = data.get("user", {})
		Api.usuario_actual = user_data if user_data is Dictionary else {}
		label_mensaje.text = "Inicio de sesión exitoso. Redirigiendo"
		await get_tree().create_timer(0.5).timeout
		Navegacion.ir_a("mainmenu")
	else:
		label_mensaje.text = Api.mensaje_error(response, "Correo o contraseña incorrecta. Intente otra vez")
