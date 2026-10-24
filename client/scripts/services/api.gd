extends Node

const DIRECCION := "http://localhost:3000" #Direccion de envio de datos
const MOCKING := true #Para enviar datos de prueba.

var token := "" #Dato de inicio de sesion

func enviar(method: int, path: String, body: Dictionary = {}) -> Dictionary:
	if MOCKING: #Evalua si MOCKING = true para retornar datos de prueba
		return {
			"ok":true,
			"codigo":123,
			"dato": {"mensaje": "MENSAJE DE PRUEBA"}
			}
	else:
		return {}
	
	var http := HTTPRequest.new()
	add_child(http) #Agregarlo como hijo permite que se ejecute la peticion
	var header := ["Content-Type: application/json"] #Header del HTTP request
	if token != "":
		header.append("Authorization: Bearer " + token)
		
	var error := http.request(DIRECCION + path, header, method, JSON.stringify(body)) #Envio de la peticion HTTP
	if error != OK: #Validar si hubo error en el envio, si es asi, se descarta la peticion y se retorna un mensaje de error
		http.queue_free()
		return {
			"ok": false,
			"codigo": 0,
			"dato": {"mensaje": "No se pudo conectar con el servidor"}
			}
	
	var response = await http.request_completed #Formato de respuesta: [resultado, codigo, header, body]
	http.queue_free()
	var datos = JSON.parse_string(response[3].get_string_from_utf8()) #Extraccion de datos del body
	if datos == null:
		datos = {}
	return {
		"ok": response[1] >= 200 and response[1] < 300,
		"codigo": response[1],
		"dato": datos
		}
