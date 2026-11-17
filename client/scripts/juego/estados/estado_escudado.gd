class_name EstadoEscudado
extends EstadoJugador
## Se mueve y actúa normal, pero ningún guardián lo afecta mientras dure el escudo.

var _restante: float = ReglasPartida.ESCUDO_S


func _init() -> void:
	nombre = "escudado"


func actualizar(jugador: ModeloJugador, delta: float) -> void:
	_restante -= delta
	if _restante <= 0.0:
		jugador.cambiar_estado(EstadoNormal.new())


func puede_ser_golpeado() -> bool:
	return false
