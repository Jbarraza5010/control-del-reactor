class_name TablaPosiciones
extends RefCounted
## Segundo observador del Marcador: arma la tabla en tiempo real y avisa al HUD con
## una sola señal, así la pantalla no tiene que ordenar nada.

signal tabla_actualizada(filas: Array)

var _marcador: Marcador


func _init(marcador: Marcador) -> void:
	_marcador = marcador
	_marcador.puntaje_cambiado.connect(_al_cambiar_puntaje)


func filas() -> Array[Dictionary]:
	return _marcador.clasificacion()


func _al_cambiar_puntaje(_jugador_id: int, _total: int, _delta: int, _fuente: int) -> void:
	tabla_actualizada.emit(_marcador.clasificacion())
