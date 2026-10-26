class_name PanelHardware
extends Node
## Conecta el juego con el panel físico a través del backend (contrato en hardware/PROTOCOL.md).
##
## 1. Vincula el panel con el código de 6 dígitos que muestra el puente en su consola
##    (POST /api/v1/hardware/link).
## 2. Abre el WebSocket /api/v1/hardware/ws y convierte cada botón del panel en una acción de
##    Input (mover_arriba, mover_abajo, mover_izquierda, mover_derecha, accion). Así el jugador
##    se mueve igual que con el teclado, sin cambiar jugador.gd.
##
## Uso:
##   var panel := PanelHardware.new()
##   add_child(panel)
##   var r := await panel.consultar_vinculo()   # r.ok, r.codigo (HTTP; 0 = sin conexión), r.datos
##   panel.escuchar()

signal estado(mensaje: String)
signal panel_vinculado(device_id: String)
signal panel_desvinculado(device_id: String)
signal boton(nombre: String, evento: String)

const RUTA := "/api/v1/hardware"
const CIERRE_TOKEN_INVALIDO := 4401
## Botón del protocolo -> acción del InputMap que usa jugador.gd.
const ACCIONES := {
	"UP": "mover_arriba",
	"DOWN": "mover_abajo",
	"LEFT": "mover_izquierda",
	"RIGHT": "mover_derecha",
	"ACTION": "accion",
}

@export var backend_url: String = "http://localhost:8000"
## TEMPORAL mientras el login no entregue tokens: el backend toma este valor como id del jugador.
## Si existe un autoload "Sesion" con una propiedad "token", se usa ese en su lugar.
@export var token_desarrollo: String = "jugador-dev"
@export var segundos_entre_reintentos: float = 2.0

var _ws := WebSocketPeer.new()
var _escuchando := false
var _estado_anterior := WebSocketPeer.STATE_CLOSED
var _estuvo_abierto := false
var _espera := 0.0
var _presionadas := {}


func _ready() -> void:
	# Si el proyecto aún no define las acciones, se crean (sin teclas) para que el panel funcione.
	for accion in ACCIONES.values():
		if not InputMap.has_action(accion):
			InputMap.add_action(accion)


func _exit_tree() -> void:
	detener()


func token() -> String:
	var sesion := get_node_or_null("/root/Sesion")
	if sesion != null and "token" in sesion and str(sesion.get("token")) != "":
		return str(sesion.get("token"))
	return token_desarrollo


# ---- Vinculación (HTTP) ------------------------------------------------------
func consultar_vinculo() -> Dictionary:
	return await _pedir(HTTPClient.METHOD_GET, "/link")


func vincular(codigo: String) -> Dictionary:
	return await _pedir(HTTPClient.METHOD_POST, "/link", {"pairingCode": codigo.strip_edges()})


func desvincular() -> Dictionary:
	detener()
	return await _pedir(HTTPClient.METHOD_DELETE, "/link")


## Texto para mostrar al jugador a partir de una respuesta fallida.
func mensaje_error(respuesta: Dictionary) -> String:
	if respuesta.get("codigo", 0) == 0:
		return "No se pudo conectar con el backend en %s. ¿Está corriendo?" % backend_url
	var error: Dictionary = respuesta.get("datos", {}).get("error", {})
	return str(error.get("message", "Error %d del backend." % respuesta.get("codigo", 0)))


## Devuelve {"ok": bool, "codigo": int, "datos": Dictionary}. codigo = 0 si no hubo conexión.
func _pedir(metodo: HTTPClient.Method, ruta: String, cuerpo: Variant = null) -> Dictionary:
	var http := HTTPRequest.new()
	http.timeout = 5.0
	add_child(http)
	var cabeceras := PackedStringArray(["Authorization: Bearer %s" % token(), "Content-Type: application/json"])
	var texto := "" if cuerpo == null else JSON.stringify(cuerpo)
	if http.request(backend_url + RUTA + ruta, cabeceras, metodo, texto) != OK:
		http.queue_free()
		return {"ok": false, "codigo": 0, "datos": {}}
	var respuesta: Array = await http.request_completed
	http.queue_free()
	if respuesta[0] != HTTPRequest.RESULT_SUCCESS:
		return {"ok": false, "codigo": 0, "datos": {}}
	var codigo: int = respuesta[1]
	var bytes: PackedByteArray = respuesta[3]
	var datos: Variant = JSON.parse_string(bytes.get_string_from_utf8()) if bytes.size() > 0 else {}
	if typeof(datos) != TYPE_DICTIONARY:
		datos = {}
	return {"ok": codigo >= 200 and codigo < 300, "codigo": codigo, "datos": datos}


# ---- Botones en tiempo real (WebSocket) --------------------------------------
## Abre el WebSocket y lo mantiene abierto (reconecta solo si se cae).
func escuchar() -> void:
	_escuchando = true
	_estuvo_abierto = false
	_abrir()


func detener() -> void:
	_escuchando = false
	_ws.close()
	_soltar_todo()


func esta_conectado() -> bool:
	return _ws.get_ready_state() == WebSocketPeer.STATE_OPEN


func _abrir() -> void:
	_ws = WebSocketPeer.new()
	_ws.handshake_headers = PackedStringArray(["Authorization: Bearer %s" % token()])
	var url := backend_url.replace("https://", "wss://").replace("http://", "ws://") + RUTA + "/ws"
	if _ws.connect_to_url(url) != OK:
		estado.emit("No se pudo abrir la conexión con %s." % url)
	_estado_anterior = _ws.get_ready_state()
	_espera = segundos_entre_reintentos


func _process(delta: float) -> void:
	if not _escuchando:
		return
	_ws.poll()
	var actual := _ws.get_ready_state()
	if actual == WebSocketPeer.STATE_OPEN:
		if _estado_anterior != WebSocketPeer.STATE_OPEN:
			_estuvo_abierto = true
			estado.emit("Panel conectado: ya puedes moverte con los botones.")
		while _ws.get_available_packet_count() > 0:
			_procesar(_ws.get_packet().get_string_from_utf8())
	elif actual == WebSocketPeer.STATE_CLOSED:
		if _estado_anterior != WebSocketPeer.STATE_CLOSED:
			_soltar_todo()
			if _ws.get_close_code() == CIERRE_TOKEN_INVALIDO:
				_escuchando = false
				estado.emit("El backend rechazó la sesión (token inválido).")
				return
			if _estuvo_abierto:
				estado.emit("Se perdió la conexión con el backend; reintentando...")
				_estuvo_abierto = false
		_espera -= delta
		if _espera <= 0.0:
			_abrir()
			return
	_estado_anterior = actual


func _procesar(texto: String) -> void:
	var mensaje: Variant = JSON.parse_string(texto)
	if typeof(mensaje) != TYPE_DICTIONARY:
		return
	match str(mensaje.get("type", "")):
		"button":
			_aplicar_boton(str(mensaje.get("button", "")), str(mensaje.get("event", "")))
		"device.linked":
			panel_vinculado.emit(str(mensaje.get("deviceId", "")))
		"device.unlinked":
			_soltar_todo()
			panel_desvinculado.emit(str(mensaje.get("deviceId", "")))


func _aplicar_boton(nombre: String, evento: String) -> void:
	if not ACCIONES.has(nombre) or evento not in ["press", "release"]:
		return
	boton.emit(nombre, evento)
	_enviar_accion(ACCIONES[nombre], evento == "press")


## Inyecta la acción como si viniera del teclado: actualiza Input (get_vector, is_action_pressed)
## y llega a _unhandled_input (is_action_pressed("accion") en jugador.gd).
func _enviar_accion(accion: String, presionada: bool) -> void:
	if _presionadas.get(accion, false) == presionada:
		return
	_presionadas[accion] = presionada
	var evento := InputEventAction.new()
	evento.action = accion
	evento.pressed = presionada
	evento.strength = 1.0 if presionada else 0.0
	Input.parse_input_event(evento)


## Suelta las acciones presionadas (por ejemplo, si se cae la conexión con un botón apretado).
func _soltar_todo() -> void:
	for accion in _presionadas.keys():
		if _presionadas[accion]:
			_enviar_accion(accion, false)
