class_name EventoMultiplicadorPuntos
extends EventoEspecial
## "Multiplicador": todos los puntos valen más durante unos segundos.


func _init() -> void:
	tipo = "multiplicador_puntos"
	duracion_s = ReglasPartida.MULTIPLICADOR_DURACION_S


func aplicar(mods: ModificadoresPartida) -> void:
	super.aplicar(mods)
	mods.multiplicador_puntos = ReglasPartida.MULTIPLICADOR_FACTOR


func terminar(mods: ModificadoresPartida) -> void:
	mods.multiplicador_puntos = 1.0
