class_name ResultadoPartida
extends RefCounted
## Arma el resultado final en un Diccionario con claves en camelCase, listo para convertirlo
## a JSON y enviarlo al backend (misma convención que hardware/PROTOCOL.md).
## Contrato completo en docs/arquitectura/04-motor-de-partida.md.
## Las posiciones son únicas (1, 2, 3...) porque la tabla participaciones tiene
## UNIQUE(partida_id, posicion): un empate se resuelve con el desempate del Marcador.

const MOTIVO_TIEMPO := "TIEMPO"
const MOTIVO_OBJETIVO := "PUNTUACION_OBJETIVO"
const MOTIVO_ABANDONO := "ABANDONO"


static func construir(marcador: Marcador, cuentas: Dictionary, motivo: String, duracion_s: float, partida_id: String = "") -> Dictionary:
	var jugadores: Array = []
	var ganador_id: int = -1
	for fila in marcador.clasificacion():
		if fila["posicion"] == 1:
			ganador_id = fila["jugador_id"]
		jugadores.append({
			"jugadorId": fila["jugador_id"],
			"cuentaId": cuentas.get(fila["jugador_id"], ""),
			"nombre": fila["nombre"],
			"puntos": fila["puntos"],
			"posicion": fila["posicion"],
		})
	return {
		"partidaId": partida_id,
		"ganadorId": ganador_id,
		"motivo": motivo,
		"duracionSegundos": snappedf(duracion_s, 0.1),
		"jugadores": jugadores,
		"podio": jugadores.slice(0, 3),  # US-026: primer, segundo y tercer lugar
	}
