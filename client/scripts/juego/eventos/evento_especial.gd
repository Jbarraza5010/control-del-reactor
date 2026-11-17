class_name EventoEspecial
extends RefCounted
## Clase base de los eventos especiales. Un evento cambia algo de la partida durante
## "duracion_s" segundos y lo deja como estaba al terminar. Solo toca ModificadoresPartida.

var tipo: String = "evento"
var duracion_s: float = 0.0

var _restante: float = 0.0


## Se llama una vez al empezar el evento.
func aplicar(_mods: ModificadoresPartida) -> void:
	_restante = duracion_s


## Se llama una vez al terminar el evento.
func terminar(_mods: ModificadoresPartida) -> void:
	pass


## Devuelve true mientras el evento sigue activo.
func actualizar(delta: float) -> bool:
	_restante -= delta
	return _restante > 0.0
