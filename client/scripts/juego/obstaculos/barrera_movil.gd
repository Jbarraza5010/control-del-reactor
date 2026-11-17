class_name BarreraMovil
extends Obstaculo
## Barrera que va y viene entre dos puntos y siempre bloquea el paso.

signal movida(nueva_area: Rect2)

var velocidad: float
var _punto_a: Vector2
var _punto_b: Vector2
var _hacia_b: bool = true


## p_destino es la posición (esquina superior izquierda) a la que se mueve desde p_area.
func _init(p_area: Rect2, p_destino: Vector2, p_velocidad: float = 40.0) -> void:
	area = p_area
	_punto_a = p_area.position
	_punto_b = p_destino
	velocidad = p_velocidad


func actualizar(delta: float, _jugadores: Array) -> void:
	var objetivo: Vector2 = _punto_b if _hacia_b else _punto_a
	area.position = area.position.move_toward(objetivo, velocidad * delta)
	if area.position.is_equal_approx(objetivo):
		_hacia_b = not _hacia_b
	movida.emit(area)


func bloquea_paso() -> bool:
	return true
