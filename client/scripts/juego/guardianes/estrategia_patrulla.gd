class_name EstrategiaPatrulla
extends EstrategiaGuardian
## Recorre una ruta de puntos en círculo, sin importar dónde estén los jugadores.

var _ruta: Array[Vector2]
var _indice: int = 0


func _init(p_ruta: Array[Vector2]) -> void:
	_ruta = p_ruta


func nombre() -> String:
	return "patrulla"


func calcular_destino(guardian: Guardian, _jugadores: Array) -> Vector2:
	if _ruta.is_empty():
		return guardian.posicion
	if guardian.posicion.distance_to(_ruta[_indice]) < 4.0:
		_indice = (_indice + 1) % _ruta.size()
	return _ruta[_indice]
