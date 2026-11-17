class_name EstadoEliminado
extends EstadoJugador
## "Eliminado temporalmente": vuelve a su punto de inicio y espera unos segundos.
## Al terminar recupera sus golpes y regresa a Normal. No pierde los puntos que ya tenía.

var _restante: float = ReglasPartida.REAPARICION_S


func _init() -> void:
	nombre = "eliminado"


func entrar(jugador: ModeloJugador) -> void:
	jugador.reaparecer()


func salir(jugador: ModeloJugador) -> void:
	jugador.golpes = 0


func actualizar(jugador: ModeloJugador, delta: float) -> void:
	_restante -= delta
	if _restante <= 0.0:
		jugador.cambiar_estado(EstadoNormal.new())


func puede_moverse() -> bool:
	return false


func puede_actuar() -> bool:
	return false


func puede_ser_golpeado() -> bool:
	return false


func factor_velocidad() -> float:
	return 0.0
