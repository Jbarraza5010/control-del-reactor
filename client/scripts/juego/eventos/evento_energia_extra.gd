class_name EventoEnergiaExtra
extends EventoEspecial
## "Energía extra": pide que aparezcan celdas de energía nuevas en la arena.
## Es instantáneo: la arena decide dónde colocarlas al recibir la señal.


func _init() -> void:
	tipo = "energia_extra"
	duracion_s = 1.0  # solo para que el HUD alcance a mostrar el aviso


func aplicar(mods: ModificadoresPartida) -> void:
	super.aplicar(mods)
	mods.celdas_extra_solicitadas.emit(ReglasPartida.CELDAS_EXTRA)
