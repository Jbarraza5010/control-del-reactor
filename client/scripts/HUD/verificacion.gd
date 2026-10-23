extends Node

@onready var campo_codigo: LineEdit = $CenterContainer/VBoxContainer/CampoCodigo
@onready var boton_volver: Button = $CenterContainer/VBoxContainer/HBoxContainer/BotonVolver
@onready var boton_validar: Button = $CenterContainer/VBoxContainer/HBoxContainer/BotonValidar
@onready var label_mensaje: Label = $CenterContainer/VBoxContainer/Mensaje

var MOCKING := true

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	boton_volver.pressed.connect(func(): Navegacion.ir_a("auth/registro"))
	boton_validar.pressed.connect(_al_validar)

func _al_validar() -> void:
	if MOCKING:
		# Asuma un código enviado al correo: 1234
		var secretKey := "1234"
		if campo_codigo.text == secretKey:
			label_mensaje.text = "Se ha validado el correo. Redirigiendo..."
			await get_tree().create_timer(0.5).timeout
			Navegacion.ir_a("entrada")
		else:
			label_mensaje.text = "No se ha validado el correo: Intente otra vez"
