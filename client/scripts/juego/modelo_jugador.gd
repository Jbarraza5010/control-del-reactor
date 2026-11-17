class_name ModeloJugador
extends RefCounted
## Datos y reglas de un jugador dentro de la partida (sin nodos de Godot).
## Es el "contexto" del patrón State: delega en EstadoJugador lo que cambia según el estado.
## jugador.gd (CharacterBody2D) solo debe leer velocidad_actual() / puede_moverse().

signal estado_cambiado(jugador_id: int, nombre_estado: String)
## La arena escucha esto para llevar al jugador a su punto de aparición.
signal reaparece(jugador_id: int, punto: Vector2)

var id: int  # identificador dentro de la partida (por ejemplo, el peer id de la red)
var nombre: String
var cuenta_id: String = ""  # id de la cuenta en el backend (para guardar el resultado)
var posicion: Vector2 = Vector2.ZERO
var punto_aparicion: Vector2 = Vector2.ZERO
var golpes: int = 0
var velocidad_base: float = ReglasPartida.VELOCIDAD_BASE

var _estado: EstadoJugador
var _modificadores: Dictionary = {}  # fuente (String) -> factor de velocidad


func _init(p_id: int, p_nombre: String, p_aparicion: Vector2 = Vector2.ZERO) -> void:
	id = p_id
	nombre = p_nombre
	punto_aparicion = p_aparicion
	posicion = p_aparicion
	_estado = EstadoNormal.new()
	_estado.entrar(self)


# ---- Delegación al estado actual ----
func cambiar_estado(nuevo: EstadoJugador) -> void:
	_estado.salir(self)
	_estado = nuevo
	_estado.entrar(self)
	estado_cambiado.emit(id, _estado.nombre)


func actualizar(delta: float) -> void:
	_estado.actualizar(self, delta)


func nombre_estado() -> String:
	return _estado.nombre


func puede_moverse() -> bool:
	return _estado.puede_moverse()


func puede_actuar() -> bool:
	return _estado.puede_actuar()


func esta_eliminado() -> bool:
	return _estado is EstadoEliminado


func puede_ser_golpeado_ahora() -> bool:
	return _estado.puede_ser_golpeado()


## Devuelve true si el golpe tuvo efecto (un jugador aturdido, escudado o eliminado no lo recibe).
func recibir_golpe() -> bool:
	if not _estado.puede_ser_golpeado():
		return false
	_estado.al_recibir_golpe(self)
	return true


## El escudo solo se puede activar desde el estado normal.
func activar_escudo() -> bool:
	if _estado is EstadoNormal:
		cambiar_estado(EstadoEscudado.new())
		return true
	return false


# ---- Velocidad ----
func velocidad_actual() -> float:
	var factor: float = _estado.factor_velocidad()
	for f in _modificadores.values():
		factor *= f
	return velocidad_base * factor


## Lo usan las trampas: cada fuente deja su propio factor y lo quita al salir.
func poner_modificador(fuente: String, factor: float) -> void:
	_modificadores[fuente] = factor


func quitar_modificador(fuente: String) -> void:
	_modificadores.erase(fuente)


func reaparecer() -> void:
	posicion = punto_aparicion
	_modificadores.clear()
	reaparece.emit(id, punto_aparicion)
