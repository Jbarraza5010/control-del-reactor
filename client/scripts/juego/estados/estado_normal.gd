class_name EstadoNormal
extends EstadoJugador
## Estado "Normal-Activo". Un golpe lo aturde; el tercer golpe lo elimina temporalmente.


func _init() -> void:
	nombre = "normal"


func al_recibir_golpe(jugador: ModeloJugador) -> void:
	jugador.golpes += 1
	if jugador.golpes >= ReglasPartida.GOLPES_PARA_ELIMINAR:
		jugador.cambiar_estado(EstadoEliminado.new())
	else:
		jugador.cambiar_estado(EstadoAturdido.new())
