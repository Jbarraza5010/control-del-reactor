extends Control

@onready var nombre_jugador: Label = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/NombreJugador
@onready var dato_partidas_jugadas: DatoEstadistica = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/HBoxContainer/DatoEstadistica
@onready var dato_partidas_ganadas: DatoEstadistica = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/HBoxContainer/DatoEstadistica2
@onready var dato_puntos_totales: DatoEstadistica = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/HBoxContainer/DatoEstadistica3
@onready var boton_volver: Button = $CenterContainer/ColorRect/MarginContainer/VBoxContainer/BotonVolver

func _ready() -> void:
	boton_volver.pressed.connect(func(): Navegacion.ir_a("mainmenu"))
	_cargar_perfil()

func _cargar_perfil() -> void:
	nombre_jugador.text = "Cargando perfil..."
	var response: Dictionary = await Api.get_json("/api/v1/auth/profile")

	if response.get("ok", false):
		var data: Dictionary = response.get("data", {})
		nombre_jugador.text = str(data.get("nombre_usuario", "JUGADOR"))
		dato_partidas_jugadas.actualizar("Partidas Jugadas", data.get("partidas_jugadas", 0))
		dato_partidas_ganadas.actualizar("Partidas Ganadas", data.get("partidas_ganadas", 0))
		dato_puntos_totales.actualizar("Total de puntos", data.get("puntos_totales", 0))
	else:
		nombre_jugador.text = Api.mensaje_error(response, "No se pudo cargar el perfil.")
