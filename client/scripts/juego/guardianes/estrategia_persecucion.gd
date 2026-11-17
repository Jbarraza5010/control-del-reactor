class_name EstrategiaPersecucion
extends EstrategiaGuardian
## Persigue al jugador vulnerable más cercano dentro de su radio de detección.
## Si no hay ninguno, vuelve al punto donde empezó.

var radio_deteccion: float


func _init(p_radio: float = ReglasPartida.RADIO_DETECCION) -> void:
	radio_deteccion = p_radio


func nombre() -> String:
	return "persecucion"


func calcular_destino(guardian: Guardian, jugadores: Array) -> Vector2:
	var mejor: ModeloJugador = null
	var mejor_distancia: float = radio_deteccion
	for jugador: ModeloJugador in jugadores:
		# Un jugador escudado, aturdido o eliminado no se persigue.
		if not jugador.puede_ser_golpeado_ahora():
			continue
		var d: float = guardian.posicion.distance_to(jugador.posicion)
		if d <= mejor_distancia:
			mejor_distancia = d
			mejor = jugador
	if mejor == null:
		return guardian.posicion_inicial
	return mejor.posicion
