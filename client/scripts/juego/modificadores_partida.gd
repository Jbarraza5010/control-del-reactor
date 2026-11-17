class_name ModificadoresPartida
extends RefCounted
## Valores que los eventos especiales cambian durante un rato y que el resto del juego
## consulta. Así un evento no necesita conocer la Partida completa (ver ADR-010).

## Un evento de "energía extra" pide celdas; la arena (cliente/host) decide dónde ponerlas.
signal celdas_extra_solicitadas(cantidad: int)

var multiplicador_reactor: float = 1.0  # sobrecarga del reactor
var multiplicador_puntos: float = 1.0  # multiplicador temporal para todo


func restablecer() -> void:
	multiplicador_reactor = 1.0
	multiplicador_puntos = 1.0
