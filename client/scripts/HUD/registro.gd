extends Control

@onready var campo_usuario: LineEdit = $CenterContainer/VBoxContainer/CampoUsuario
@onready var campo_correo: LineEdit = $CenterContainer/VBoxContainer/CampoCorreo
@onready var campo_contrasena: LineEdit = $CenterContainer/VBoxContainer/CampoContrasena
@onready var boton_registrar: Button = $CenterContainer/VBoxContainer/HBoxContainer/BotonRegistrar
@onready var boton_volver: Button = $CenterContainer/VBoxContainer/HBoxContainer/BotonVolver
@onready var boton_ir_login: Button = $CenterContainer/VBoxContainer/BotonIrLogin
@onready var label_mensaje: Label = $CenterContainer/VBoxContainer/LabelMensaje

func _ready() -> void:
	boton_registrar.pressed.connect(_al_registrar)
	boton_ir_login.pressed.connect(func(): Navegacion.ir_a("auth/login"))
	boton_volver.pressed.connect(func(): Navegacion.ir_a("entrada"))

func _al_registrar() -> void:
	# Validaciones del frontend
	var usuario := campo_usuario.text.strip_edges()
	var correo := campo_correo.text.strip_edges()
	var contrasena := campo_contrasena.text
	
	# Validar nombre de usuario
	if ValidacionCuenta.validar_usuario(usuario) != "":
		label_mensaje.text = ValidacionCuenta.validar_usuario(usuario)
		return
	# Validar correo electronico
	if ValidacionCuenta.validar_correo(correo) != "":
		label_mensaje.text = ValidacionCuenta.validar_correo(correo)
		return
	# Validar contrasena
	if ValidacionCuenta.validar_contrasena(contrasena) != "":
		label_mensaje.text = ValidacionCuenta.validar_contrasena(contrasena)
		return
	
	# Envio de datos
	
	boton_registrar.disabled = true #Deshabilitar boton de registro hasta que se haga una validacion
	var response = await Api.enviar(HTTPClient.METHOD_POST, "/auth/registro", {
		"usuario": campo_usuario.text.strip_edges(),
		"correo": campo_correo.text.strip_edges(),
		"clave": campo_contrasena.text
	})
	boton_registrar.disabled = false
	
	if response.ok:
		Navegacion.ir_a("auth/verificacion")
	else:
		label_mensaje.text = response.datos.get("mensaje", "Ocurrio un error.")
