class_name EstadoAturdido
extends EstadoJugador
## No se mueve ni actúa durante unos segundos y no recibe más golpes mientras tanto
## (así un guardián no lo "encadena").

var _restante: float = ReglasPartida.ATURDIMIENTO_S


func _init() -> void:
	nombre = "aturdido"


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
