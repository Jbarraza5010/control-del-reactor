class_name PuertaAutomatica
extends Obstaculo
## Puerta que se abre sola cuando un jugador se acerca y se cierra unos segundos después
## de que nadie queda cerca.

signal abierta_cambiada(abierta: bool)

var abierta: bool = false
var radio_activacion: float = ReglasPartida.PUERTA_RADIO_ACTIVACION
var _cierra_en: float = 0.0


func _init(p_area: Rect2) -> void:
	area = p_area


func actualizar(delta: float, jugadores: Array) -> void:
	if _hay_jugador_cerca(jugadores):
		_cierra_en = ReglasPartida.PUERTA_ABIERTA_S
		_poner_abierta(true)
	elif abierta:
		_cierra_en -= delta
		if _cierra_en <= 0.0:
			_poner_abierta(false)


func bloquea_paso() -> bool:
	return not abierta


func _hay_jugador_cerca(jugadores: Array) -> bool:
	var centro: Vector2 = area.get_center()
	for jugador: ModeloJugador in jugadores:
		if not jugador.esta_eliminado() and jugador.posicion.distance_to(centro) <= radio_activacion:
			return true
	return false


func _poner_abierta(valor: bool) -> void:
	if abierta != valor:
		abierta = valor
		abierta_cambiada.emit(abierta)
