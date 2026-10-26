extends Node

const URL := "http://localhost:8000" # Direccion del servidor
const TIMEOUT_SEG := 10.0 # Tiempo de respuesta máximo en segundos

var token: String = "" # Token de sesión tras iniciar sesión
var usuario_actual: Dictionary = {} # Datos del jugador autenticado
var correo_pendiente: String = "" # Correo registrado pendiente de verificar

# Envío de datos al servidor (POST JSON)
func post_json(path: String, body: Dictionary) -> Dictionary:
	var respuesta: Dictionary = await enviar(HTTPClient.METHOD_POST, path, body)
	return respuesta

# Envío genérico de peticiones HTTP con cuerpo JSON
func enviar(method: HTTPClient.Method, path: String, body: Dictionary = {}) -> Dictionary:
	var http := HTTPRequest.new()
	http.timeout = TIMEOUT_SEG
	add_child(http)

	var headers: Array[String] = ["Content-Type: application/json"]
	if token != "":
		headers.append("Authorization: Bearer " + token)

	var payload: String = "" if method == HTTPClient.METHOD_GET else JSON.stringify(body)
	var err: Error = http.request(
		URL + path,
		headers,
		method,
		payload
	)
	if err != OK:
		http.queue_free()
		return _error_red()

	var res: Array = await http.request_completed   # [result, status, headers, body]
	http.queue_free()

	if res[0] != HTTPRequest.RESULT_SUCCESS:
		return _error_red()

	var status: int = res[1]
	var bytes: PackedByteArray = res[3]
	var parsed: Variant = JSON.parse_string(bytes.get_string_from_utf8()) if bytes.size() > 0 else {}
	var data: Dictionary = parsed if parsed is Dictionary else {}

	if status >= 200 and status < 300:
		return {
			"ok": true,
			"status": status,
			"codigo": status,
			"data": data,
			"datos": data,
		}

	var raw_err: Variant = data.get("error", {})
	var err_obj: Dictionary = raw_err if raw_err is Dictionary else {"code": "UNKNOWN", "message": "Error inesperado del servidor"}
	return {
		"ok": false,
		"status": status,
		"codigo": status,
		"data": data,
		"datos": data,
		"error": err_obj,
	}

func mensaje_error(respuesta: Dictionary, por_defecto: String = "Ocurrió un error.") -> String:
	var err: Variant = respuesta.get("error", {})
	if err is Dictionary and err.has("message"):
		return str(err.get("message"))
	var data: Variant = respuesta.get("data", respuesta.get("datos", {}))
	if data is Dictionary:
		if data.has("message"):
			return str(data.get("message"))
		if data.has("mensaje"):
			return str(data.get("mensaje"))
	return por_defecto

func _error_red() -> Dictionary:
	var err: Dictionary = {"code": "NETWORK_ERROR", "message": "No se pudo conectar con el servidor"}
	return {
		"ok": false,
		"status": 0,
		"codigo": 0,
		"data": {},
		"datos": {"mensaje": "No se pudo conectar con el servidor"},
		"error": err,
	}
