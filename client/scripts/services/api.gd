extends Node

const URL := "http://localhost:8000" # Direccion del servidor
const TIMEOUT_SEG := 10.0 # Tiempo de respuesta máximo en segundos

# Envío de datos al servidor
func post_json(path: String, body: Dictionary) -> Dictionary:
	var http := HTTPRequest.new()
	http.timeout = TIMEOUT_SEG
	add_child(http)

	var err := http.request(
		URL + path,
		["Content-Type: application/json"],
		HTTPClient.METHOD_POST,
		JSON.stringify(body)
	)
	if err != OK:
		http.queue_free()
		return _error_red()

	var res: Array = await http.request_completed   # [result, status, headers, body]
	http.queue_free()

	if res[0] != HTTPRequest.RESULT_SUCCESS:
		return _error_red()

	var status: int = res[1]
	var parsed = JSON.parse_string((res[3] as PackedByteArray).get_string_from_utf8())
	var data: Dictionary = parsed if parsed is Dictionary else {}

	if status >= 200 and status < 300:
		return {"ok": true, "status": status, "data": data}
	return {
		"ok": false,
		"status": status,
		"error": data.get("error", {"code": "UNKNOWN", "message": "Error inesperado del servidor"}),
	}

func _error_red() -> Dictionary:
	return {
		"ok": false,
		"status": 0,
		"error": {"code": "NETWORK_ERROR", "message": "No se pudo conectar con el servidor"},
	}
