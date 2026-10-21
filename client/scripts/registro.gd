extends Control

@onready var campo_usuario: LineEdit = $CenterContainer/VBoxContainer/CampoUsuario
@onready var campo_correo: LineEdit = $CenterContainer/VBoxContainer/CampoCorreo
@onready var campo_clave: LineEdit = $CenterContainer/VBoxContainer/CampoClave
@onready var boton_registrar: Button = $CenterContainer/VBoxContainer/HBoxContainer/BotonRegistrar
@onready var boton_volver: Button = $CenterContainer/VBoxContainer/HBoxContainer/BotonVolver
@onready var boton_ir_login: Button = $CenterContainer/VBoxContainer/BotonIrLogin
@onready var mensaje: Label = $CenterContainer/VBoxContainer/Mensaje

func _ready() -> void:
	boton_registrar.pressed.connect(_al_registrar)
	boton_ir_login.pressed.connect(func(): Navegacion.ir_a("login"))
	boton_volver.pressed.connect(func(): Navegacion.ir_a("entrada"))

func _al_registrar() -> void:
	#Validaciones de frontend
	
	#Validar nombre de usuario
	if campo_usuario.text.strip_edges() == "" or not campo_correo.text.contains("@"):
		mensaje.text = "Revisa el usuario y el correo."
		return
	#Validar contrasena de al menos 8 caracteres
	if campo_clave.text.length() < 8:
		mensaje.text = "La contraseña debe tener al menos 8 caracteres."
		return
	
	boton_registrar.disabled = true #Deshabilitar boton de registro hasta que se haga una validacion
	var response = await Api.enviar(HTTPClient.METHOD_POST, "/auth/registro", {
		"usuario": campo_usuario.text.strip_edges(),
		"correo": campo_correo.text.strip_edges(),
		"clave": campo_clave.text
	})
	boton_registrar.disabled = false
	
	if response.ok:
		Navegacion.ir_a("verificacion")
	else:
		mensaje.text = response.datos.get("mensaje", "Ocurrio un error.")
