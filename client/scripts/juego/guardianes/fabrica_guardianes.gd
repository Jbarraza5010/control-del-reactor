class_name FabricaGuardianes
extends RefCounted
## Patrón Factory (versión simple, con match): crea guardianes ya configurados.
## Quien los pide (la arena, un evento de "invasión") solo dice el tipo; no necesita
## saber qué estrategia ni qué velocidad lleva cada uno.

enum Tipo { PATRULLERO, PERSEGUIDOR }


static func crear(tipo: Tipo, posicion: Vector2, ruta: Array[Vector2] = []) -> Guardian:
	match tipo:
		Tipo.PATRULLERO:
			var puntos: Array[Vector2] = ruta.duplicate()
			if puntos.is_empty():
				puntos.append(posicion)
			return Guardian.new("patrullero", posicion, ReglasPartida.VELOCIDAD_PATRULLERO, EstrategiaPatrulla.new(puntos))
		Tipo.PERSEGUIDOR:
			return Guardian.new("perseguidor", posicion, ReglasPartida.VELOCIDAD_PERSEGUIDOR, EstrategiaPersecucion.new())
	push_error("FabricaGuardianes: tipo desconocido")
	return null
