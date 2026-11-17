class_name TrampaLentitud
extends Obstaculo
## Zona del suelo que reduce la velocidad de quien la pisa. No bloquea el paso.

var factor: float = ReglasPartida.FACTOR_TRAMPA
var _fuente: String


func _init(p_area: Rect2, p_factor: float = ReglasPartida.FACTOR_TRAMPA) -> void:
	area = p_area
	factor = p_factor
	# Cada trampa usa su propia clave para que dos trampas no se pisen entre sí.
	_fuente = "trampa_%d" % get_instance_id()


func actualizar(_delta: float, jugadores: Array) -> void:
	for jugador: ModeloJugador in jugadores:
		if area.has_point(jugador.posicion):
			jugador.poner_modificador(_fuente, factor)
		else:
			jugador.quitar_modificador(_fuente)
