class_name EstrategiaGuardian
extends RefCounted
## Interfaz del patrón Strategy: decide HACIA DÓNDE se mueve un guardián.
## El guardián no sabe cómo se decide; solo pide el destino y avanza.


func nombre() -> String:
	return "base"


func calcular_destino(guardian: Guardian, _jugadores: Array) -> Vector2:
	return guardian.posicion
