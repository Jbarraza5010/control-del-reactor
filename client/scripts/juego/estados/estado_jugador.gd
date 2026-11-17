class_name EstadoJugador
extends RefCounted
## Interfaz del patrón State. Cada estado decide qué puede hacer el jugador y a qué estado
## pasa. Los métodos con "_" no usados se dejan vacíos a propósito: cada subclase sobrescribe
## solo lo que le interesa.

var nombre: String = "base"


func entrar(_jugador: ModeloJugador) -> void:
	pass


func salir(_jugador: ModeloJugador) -> void:
	pass


## Se llama en cada tick de la partida (solo en el anfitrión).
func actualizar(_jugador: ModeloJugador, _delta: float) -> void:
	pass


func puede_moverse() -> bool:
	return true


## "Actuar" = usar el botón ACCIÓN (extraer energía, activar terminales).
func puede_actuar() -> bool:
	return true


func puede_ser_golpeado() -> bool:
	return true


func factor_velocidad() -> float:
	return 1.0


## Solo se llama si puede_ser_golpeado() es true.
func al_recibir_golpe(_jugador: ModeloJugador) -> void:
	pass
