class_name EventoSobrecargaReactor
extends EventoEspecial
## "Sobrecarga": el reactor genera el doble de energía mientras dura.


func _init() -> void:
	tipo = "sobrecarga_reactor"
	duracion_s = ReglasPartida.SOBRECARGA_DURACION_S


func aplicar(mods: ModificadoresPartida) -> void:
	super.aplicar(mods)
	mods.multiplicador_reactor = ReglasPartida.SOBRECARGA_FACTOR


func terminar(mods: ModificadoresPartida) -> void:
	mods.multiplicador_reactor = 1.0
