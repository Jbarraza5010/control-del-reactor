class_name Obstaculo
extends RefCounted
## Clase base de los obstáculos de la arena. La lógica vive aquí; la escena de Godot
## solo dibuja el rectángulo (area) y, si bloquea_paso(), activa su colisión.

## Zona que ocupa el obstáculo, en coordenadas del mundo.
var area: Rect2 = Rect2()


func actualizar(_delta: float, _jugadores: Array) -> void:
	pass


## true = los jugadores no pueden atravesarlo en este momento.
func bloquea_paso() -> bool:
	return false
