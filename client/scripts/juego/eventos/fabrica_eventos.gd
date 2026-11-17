class_name FabricaEventos
extends RefCounted
## Patrón Factory (versión simple, con match): crea el evento especial pedido.
## Para agregar un evento nuevo (por ejemplo "apagón") se crea su clase y se suma
## una línea aquí; el programador y la partida no cambian (Open/Closed).

enum Tipo { SOBRECARGA_REACTOR, ENERGIA_EXTRA, MULTIPLICADOR_PUNTOS }


static func crear(tipo: Tipo) -> EventoEspecial:
	match tipo:
		Tipo.SOBRECARGA_REACTOR:
			return EventoSobrecargaReactor.new()
		Tipo.ENERGIA_EXTRA:
			return EventoEnergiaExtra.new()
		Tipo.MULTIPLICADOR_PUNTOS:
			return EventoMultiplicadorPuntos.new()
	push_error("FabricaEventos: tipo desconocido")
	return null


static func crear_aleatorio(rng: RandomNumberGenerator) -> EventoEspecial:
	var tipos: Array = Tipo.values()
	return crear(tipos[rng.randi_range(0, tipos.size() - 1)])
