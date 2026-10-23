extends Node2D

@onready var boton_volver: Button = $CanvasLayer/HBoxContainer/BotonVolver
@onready var boton_detectar: Button = $CanvasLayer/HBoxContainer/BotonDetectar
@onready var indicacion: Label = $"CanvasLayer/TituloIndicación"

var _panel: PanelHardware


func _ready() -> void:
	boton_volver.pressed.connect(func(): Navegacion.ir_a("mainmenu"))
	boton_detectar.pressed.connect(_detectar_panel_fisico)
	_panel = PanelHardware.new()
	add_child(_panel)
	_panel.estado.connect(_mostrar)
	_panel.panel_desvinculado.connect(func(_device_id: String): _mostrar("El panel se desvinculó."))


## Si el jugador ya tiene panel, se conecta; si no, pide el código que muestra el puente.
func _detectar_panel_fisico() -> void:
	boton_detectar.disabled = true
	_mostrar("Buscando tu panel...")
	var respuesta := await _panel.consultar_vinculo()
	boton_detectar.disabled = false
	if respuesta.ok:
		_mostrar("Panel %s vinculado. Conectando..." % respuesta.datos.get("deviceId", ""))
		_panel.escuchar()
	elif respuesta.codigo == 404:
		_pedir_codigo()
	else:
		_mostrar(_panel.mensaje_error(respuesta))


func _pedir_codigo() -> void:
	var dialogo := ConfirmationDialog.new()
	dialogo.title = "Vincular panel físico"
	dialogo.ok_button_text = "Vincular"
	var caja := VBoxContainer.new()
	var texto := Label.new()
	texto.text = "Escribe el código de 6 dígitos que muestra el puente en su consola:"
	var campo := LineEdit.new()
	campo.max_length = 6
	campo.placeholder_text = "000000"
	caja.add_child(texto)
	caja.add_child(campo)
	dialogo.add_child(caja)
	$CanvasLayer.add_child(dialogo)
	dialogo.confirmed.connect(func():
		_vincular(campo.text)
		dialogo.queue_free()
	)
	dialogo.canceled.connect(dialogo.queue_free)
	campo.text_submitted.connect(func(_texto: String):
		_vincular(campo.text)
		dialogo.queue_free()
	)
	dialogo.popup_centered(Vector2i(460, 130))
	campo.grab_focus()


func _vincular(codigo: String) -> void:
	_mostrar("Vinculando...")
	var respuesta := await _panel.vincular(codigo)
	if respuesta.ok:
		_mostrar("Panel %s vinculado. Conectando..." % respuesta.datos.get("deviceId", ""))
		_panel.escuchar()
	else:
		_mostrar(_panel.mensaje_error(respuesta))


func _mostrar(mensaje: String) -> void:
	indicacion.text = mensaje
