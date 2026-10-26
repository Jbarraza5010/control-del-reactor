extends Control

@onready var campo_codigo: LineEdit = $CenterContainer/VBoxContainer/CampoCodigo
@onready var boton_volver: Button = $CenterContainer/VBoxContainer/HBoxContainer/BotonVolver
@onready var boton_validar: Button = $CenterContainer/VBoxContainer/HBoxContainer/BotonValidar
@onready var label_mensaje: Label = $CenterContainer/VBoxContainer/Mensaje

func _ready() -> void:
	boton_volver.pressed.connect(func(): Navegacion.ir_a("auth/registro"))
	boton_validar.pressed.connect(_al_validar)

func _al_validar() -> void:
	# Validaciones en cliente
	var codigo: String = campo_codigo.text.strip_edges()
	var err_codigo: String = ValidacionCuenta.validar_codigo(codigo)
	if err_codigo != "":
		label_mensaje.text = err_codigo
		return

	var payload: Dictionary = {"code": codigo}
	if Api.correo_pendiente != "":
		payload["email"] = Api.correo_pendiente

	boton_validar.disabled = true
	var response: Dictionary = await Api.post_json("/api/v1/auth/verify-email", payload)
	boton_validar.disabled = false

	if response.get("ok", false):
		Api.correo_pendiente = ""
		label_mensaje.text = "Se ha validado el correo. Redirigiendo..."
		await get_tree().create_timer(0.5).timeout
		Navegacion.ir_a("auth/login")
	else:
		label_mensaje.text = Api.mensaje_error(response, "No se ha validado el correo: Intente otra vez")
