class_name ProgramadorEventos
extends RefCounted
## Lanza un evento aleatorio cada cierto tiempo (uno a la vez). Corre solo en el anfitrión;
## los clientes se enteran por las señales que la Partida reenvía (ver ADR-009).

signal evento_iniciado(tipo: String, duracion: float)
signal evento_terminado(tipo: String)

var evento_activo: EventoEspecial = null

var _rng := RandomNumberGenerator.new()
var _cuenta_regresiva: float = 0.0


## Con una semilla fija (distinta de 0) la secuencia de eventos se repite: sirve para pruebas.
func _init(semilla: int = 0) -> void:
	if semilla != 0:
		_rng.seed = semilla
	else:
		_rng.randomize()
	_reiniciar_cuenta()


func actualizar(delta: float, mods: ModificadoresPartida) -> void:
	if evento_activo != null:
		if not evento_activo.actualizar(delta):
			var tipo := evento_activo.tipo
			evento_activo.terminar(mods)
			evento_activo = null
			evento_terminado.emit(tipo)
			_reiniciar_cuenta()
		return
	_cuenta_regresiva -= delta
	if _cuenta_regresiva <= 0.0:
		lanzar(FabricaEventos.crear_aleatorio(_rng), mods)


## Se puede llamar directo (por ejemplo desde una prueba o un evento forzado).
func lanzar(evento: EventoEspecial, mods: ModificadoresPartida) -> void:
	evento_activo = evento
	evento.aplicar(mods)
	evento_iniciado.emit(evento.tipo, evento.duracion_s)


func _reiniciar_cuenta() -> void:
	_cuenta_regresiva = _rng.randf_range(ReglasPartida.INTERVALO_EVENTOS_MIN_S, ReglasPartida.INTERVALO_EVENTOS_MAX_S)
