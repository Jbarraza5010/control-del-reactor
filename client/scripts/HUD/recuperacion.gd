extends Node

@onready var campo_correo: LineEdit = $CenterContainer/VBoxContainer/HBoxContainer/CampoCorreo
@onready var boton_enviar_codigo: Button = $CenterContainer/VBoxContainer/HBoxContainer/BotonEnviarCodigo
@onready var campo_codigo: LineEdit = $CenterContainer/VBoxContainer/CampoCodigo
@onready var boton_volver: Button = $CenterContainer/VBoxContainer/HBoxContainer2/BotonVolver
@onready var boton_validar: Button = $CenterContainer/VBoxContainer/HBoxContainer2/BotonValidar
@onready var label_mensaje: Label = $CenterContainer/VBoxContainer/Mensaje

var MOCKING := true
var OTP : String
var MOCKCORREO : String

func _ready() -> void:
	boton_volver.pressed.connect(func(): Navegacion.ir_a("auth/login"))
	boton_enviar_codigo.pressed.connect(_enviar_codigo)
	boton_validar.pressed.connect(_enviar_clave_al_correo)

func _enviar_codigo() -> void:
	if MOCKING:
		# Asuma que se envia código de un solo uso al correo test@testing.com
		MOCKCORREO = "test@testing.com"
		if campo_correo.text == MOCKCORREO:
			OTP = "1234"
			label_mensaje.text = "Se ha enviado un código de un solo uso al correo %s" % MOCKCORREO
		else:
			label_mensaje.text = "SE ESTA UTILIZANDO MOCKING. INTRODUZCA EL CORREO DOCUMENTADO"

func _enviar_clave_al_correo() -> void:
	if MOCKING:
		# Asuma que se envia la contrasena de la cuenta: 12345678
		label_mensaje.text = "Se ha enviado el correo a %s" % MOCKCORREO
		if campo_codigo.text == OTP:
			label_mensaje.text = "Se ha enviado la contraseña a %s. Redirigiendo..." % MOCKCORREO
			await get_tree().create_timer(0.5).timeout
			Navegacion.ir_a("auth/login")
		else:
			label_mensaje.text = "No se ha validado el correo. Intente otra vez"
			
		
	
