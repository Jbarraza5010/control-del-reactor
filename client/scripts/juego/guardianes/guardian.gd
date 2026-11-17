class_name Guardian
extends RefCounted
## Guardián automático que protege el reactor. Es el "contexto" del patrón Strategy:
## su comportamiento de movimiento lo da la EstrategiaGuardian que tenga asignada,
## y se puede cambiar mientras la partida corre (por ejemplo, en un evento de invasión).

## La Partida escucha esto para restar energía al jugador alcanzado.
signal alcanzo_jugador(guardian_id: int, jugador_id: int)

var id: int = 0  # lo asigna la Partida al agregarlo
var tipo: String = "guardian"
var posicion: Vector2
var posicion_inicial: Vector2
var velocidad: float
var radio_contacto: float = ReglasPartida.RADIO_CONTACTO
var penalizacion: int = ReglasPartida.PENALIZACION_GUARDIAN

var _estrategia: EstrategiaGuardian


func _init(p_tipo: String, p_posicion: Vector2, p_velocidad: float, p_estrategia: EstrategiaGuardian) -> void:
	tipo = p_tipo
	posicion = p_posicion
	posicion_inicial = p_posicion
	velocidad = p_velocidad
	_estrategia = p_estrategia


func cambiar_estrategia(nueva: EstrategiaGuardian) -> void:
	_estrategia = nueva


func nombre_estrategia() -> String:
	return _estrategia.nombre()


func actualizar(delta: float, jugadores: Array) -> void:
	var destino: Vector2 = _estrategia.calcular_destino(self, jugadores)
	posicion = posicion.move_toward(destino, velocidad * delta)
	_revisar_contacto(jugadores)


func _revisar_contacto(jugadores: Array) -> void:
	for jugador: ModeloJugador in jugadores:
		if posicion.distance_to(jugador.posicion) <= radio_contacto and jugador.recibir_golpe():
			alcanzo_jugador.emit(id, jugador.id)
