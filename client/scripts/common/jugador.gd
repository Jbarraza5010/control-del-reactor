extends CharacterBody2D
# Movimiento cenital + interacción con objetos dibujados en un TileMapLayer.

@export var velocidad: float = 100.0

# Arrastra aquí, desde el Inspector, el nodo TileMapLayer del mapa.
@export var mapa: TileMapLayer

# Distancia máxima para interactuar, medida en CELDAS (no en píxeles).
# 1 = la celda donde estoy parado y las 8 que la rodean.
@export var alcance_en_celdas: int = 1

# Diccionario: "si el tile está en estas coordenadas del atlas, cámbialo
# a estas otras". Las coordenadas (columna, fila) las ves en el editor de
# TileSet, en la imagen del atlas. AJUSTA estos números a tu tileset.
# Ejemplo: palanca apagada (3, 0) <-> palanca encendida (4, 0).
var transiciones: Dictionary = {
	Vector2i(3, 0): Vector2i(4, 0),
	Vector2i(4, 0): Vector2i(3, 0),
}


func _physics_process(_delta: float) -> void:
	var direccion: Vector2 = Input.get_vector(
		"mover_izquierda", "mover_derecha", "mover_arriba", "mover_abajo"
	)
	velocity = direccion * velocidad
	move_and_slide()


# _unhandled_input se llama solo cuando ocurre un evento de entrada
# (una tecla, un botón...). Así no revisamos el botón 60 veces por segundo.
func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("accion"):
		_interactuar()


func _interactuar() -> void:
	if mapa == null:
		push_warning("No se asignó el TileMapLayer en el Inspector.")
		return

	# 1. Convertir mi posición en el mundo a una celda del mapa.
	#    to_local: de coordenadas del mundo a coordenadas del mapa.
	#    local_to_map: de coordenadas del mapa a (columna, fila) de celda.
	var celda_jugador: Vector2i = mapa.local_to_map(mapa.to_local(global_position))

	# 2. Buscar, entre las celdas cercanas, la más próxima que sea interactuable.
	var celda_objetivo: Vector2i = Vector2i(-1, -1)
	var mejor_distancia: float = INF
	var encontrada: bool = false

	for dx in range(-alcance_en_celdas, alcance_en_celdas + 1):
		for dy in range(-alcance_en_celdas, alcance_en_celdas + 1):
			var celda: Vector2i = celda_jugador + Vector2i(dx, dy)
			# Qué dibujo (tile) hay en esa celda. Si está vacía devuelve (-1, -1).
			var coords_atlas: Vector2i = mapa.get_cell_atlas_coords(celda)

			if transiciones.has(coords_atlas):
				var distancia: float = Vector2(dx, dy).length()
				if distancia < mejor_distancia:
					mejor_distancia = distancia
					celda_objetivo = celda
					encontrada = true

	if not encontrada:
		return  # No hay nada interactuable cerca.

	# 3. Cambiar el tile por su nuevo estado.
	var origen: int = mapa.get_cell_source_id(celda_objetivo)
	var actual: Vector2i = mapa.get_cell_atlas_coords(celda_objetivo)
	mapa.set_cell(celda_objetivo, origen, transiciones[actual])
