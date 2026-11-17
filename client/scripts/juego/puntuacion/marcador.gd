class_name Marcador
extends RefCounted
## Sistema de puntuación. Es el "sujeto" del patrón Observer: cuando cambia un puntaje
## emite señales y quienes escuchan (HUD, TablaPosiciones, la Partida) reaccionan sin que
## el marcador sepa quiénes son. Las señales de Godot son la implementación del Observer.

signal puntaje_cambiado(jugador_id: int, total: int, delta: int, fuente: int)
signal objetivo_alcanzado(jugador_id: int)

var objetivo: int
## La Partida lo actualiza en cada tick; se usa para desempatar (gana quien llegó primero).
var tiempo_actual: float = 0.0

var _puntos: Dictionary = {}  # jugador_id -> int
var _nombres: Dictionary = {}  # jugador_id -> String
var _ultimo_cambio: Dictionary = {}  # jugador_id -> float (tiempo en que subió por última vez)
var _mods: ModificadoresPartida
var _objetivo_avisado: bool = false


func _init(p_mods: ModificadoresPartida, p_objetivo: int = ReglasPartida.PUNTUACION_OBJETIVO) -> void:
	_mods = p_mods
	objetivo = p_objetivo


func registrar_jugador(jugador_id: int, nombre: String) -> void:
	_puntos[jugador_id] = 0
	_nombres[jugador_id] = nombre
	_ultimo_cambio[jugador_id] = 0.0


## Suma puntos aplicando los multiplicadores activos. Devuelve los puntos realmente sumados.
func sumar(jugador_id: int, base: int, fuente: ReglasPartida.FuentePuntos) -> int:
	if not _puntos.has(jugador_id):
		push_warning("Marcador: jugador %d no registrado" % jugador_id)
		return 0
	var factor: float = _mods.multiplicador_puntos
	if fuente == ReglasPartida.FuentePuntos.REACTOR:
		factor *= _mods.multiplicador_reactor
	var delta: int = roundi(base * factor)
	_puntos[jugador_id] += delta
	_ultimo_cambio[jugador_id] = tiempo_actual
	puntaje_cambiado.emit(jugador_id, _puntos[jugador_id], delta, fuente)
	if not _objetivo_avisado and _puntos[jugador_id] >= objetivo:
		_objetivo_avisado = true
		objetivo_alcanzado.emit(jugador_id)
	return delta


## Resta energía (penalización de un guardián). Nunca baja de 0.
func restar(jugador_id: int, cantidad: int) -> int:
	if not _puntos.has(jugador_id):
		return 0
	var antes: int = _puntos[jugador_id]
	_puntos[jugador_id] = maxi(0, antes - cantidad)
	var delta: int = _puntos[jugador_id] - antes
	if delta != 0:
		puntaje_cambiado.emit(jugador_id, _puntos[jugador_id], delta, ReglasPartida.FuentePuntos.EVENTO)
	return delta


func puntos_de(jugador_id: int) -> int:
	return _puntos.get(jugador_id, 0)


## Lista ordenada de mayor a menor. Empate: primero quien llegó antes a ese puntaje.
func clasificacion() -> Array[Dictionary]:
	var filas: Array[Dictionary] = []
	for id in _puntos:
		filas.append({"jugador_id": id, "nombre": _nombres[id], "puntos": _puntos[id], "momento": _ultimo_cambio[id]})
	filas.sort_custom(
		func(a: Dictionary, b: Dictionary) -> bool:
			if a["puntos"] != b["puntos"]:
				return a["puntos"] > b["puntos"]
			return a["momento"] < b["momento"]
	)
	for i in filas.size():
		filas[i]["posicion"] = i + 1
	return filas
