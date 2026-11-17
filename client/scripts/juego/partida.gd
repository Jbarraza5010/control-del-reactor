class_name Partida
extends RefCounted
## Coordina una partida completa: jugadores, guardianes, obstáculos, eventos, puntuación,
## temporizador y fin de partida. Solo la ejecuta el ANFITRIÓN (ADR-009); los clientes
## reciben el estado por la red y lo dibujan.
##
## Uso desde la escena del anfitrión (por ejemplo, en _physics_process):
##   partida.actualizar(delta)
## Y cuando el jugador hace algo que da puntos (lo llama el reactor, la celda o la terminal):
##   partida.registrar_puntos(jugador_id, ReglasPartida.FuentePuntos.CELDA)

enum Estado { ESPERANDO, EN_CURSO, FINALIZADA }

signal partida_iniciada
signal partida_finalizada(resultado: Dictionary)
signal tiempo_cambiado(segundos_restantes: int)
signal evento_iniciado(tipo: String, duracion: float)
signal evento_terminado(tipo: String)
signal penalizacion_aplicada(jugador_id: int, guardian_id: int, energia_perdida: int)

var modificadores := ModificadoresPartida.new()
var marcador: Marcador
var tabla: TablaPosiciones
var tiempo_limite: float
## Id de la partida en el backend (lo entrega el endpoint de crear partida). Viaja en el
## resultado para que el backend pueda rechazar un guardado repetido.
var partida_id: String = ""

var _jugadores: Dictionary = {}  # id -> ModeloJugador (los que siguen conectados)
var _cuentas: Dictionary = {}  # id -> cuenta_id (se conserva aunque se desconecten)
var _guardianes: Array[Guardian] = []
var _obstaculos: Array[Obstaculo] = []
var _programador: ProgramadorEventos
var _estado: Estado = Estado.ESPERANDO
var _transcurrido: float = 0.0
var _segundo_anunciado: int = -1
var _siguiente_id_guardian: int = 1
var _resultado: Dictionary = {}  # vacío hasta que la partida finaliza (US-026)


func _init(p_tiempo_limite: float = ReglasPartida.TIEMPO_LIMITE_S, p_objetivo: int = ReglasPartida.PUNTUACION_OBJETIVO, semilla: int = 0) -> void:
	tiempo_limite = p_tiempo_limite
	marcador = Marcador.new(modificadores, p_objetivo)
	tabla = TablaPosiciones.new(marcador)
	_programador = ProgramadorEventos.new(semilla)
	marcador.objetivo_alcanzado.connect(_al_alcanzar_objetivo)
	_programador.evento_iniciado.connect(func(t: String, d: float) -> void: evento_iniciado.emit(t, d))
	_programador.evento_terminado.connect(func(t: String) -> void: evento_terminado.emit(t))


# ---- Armado de la partida (antes de iniciar) ----
func agregar_jugador(id: int, nombre: String, aparicion: Vector2, cuenta_id: String = "") -> ModeloJugador:
	if _estado != Estado.ESPERANDO or _jugadores.size() >= ReglasPartida.JUGADORES_MAX:
		return null
	var jugador := ModeloJugador.new(id, nombre, aparicion)
	jugador.cuenta_id = cuenta_id
	_jugadores[id] = jugador
	_cuentas[id] = cuenta_id
	marcador.registrar_jugador(id, nombre)
	return jugador


func agregar_guardian(guardian: Guardian) -> void:
	guardian.id = _siguiente_id_guardian
	_siguiente_id_guardian += 1
	guardian.alcanzo_jugador.connect(_al_alcanzar_guardian.bind(guardian))
	_guardianes.append(guardian)


func agregar_obstaculo(obstaculo: Obstaculo) -> void:
	_obstaculos.append(obstaculo)


## Devuelve false si todavía no hay suficientes jugadores.
func iniciar() -> bool:
	if _estado != Estado.ESPERANDO or _jugadores.size() < ReglasPartida.JUGADORES_MIN:
		return false
	_estado = Estado.EN_CURSO
	partida_iniciada.emit()
	return true


# ---- Ciclo de juego ----
func actualizar(delta: float) -> void:
	if _estado != Estado.EN_CURSO:
		return
	_transcurrido += delta
	marcador.tiempo_actual = _transcurrido
	var lista: Array = _jugadores.values()
	for jugador: ModeloJugador in lista:
		jugador.actualizar(delta)
	for obstaculo in _obstaculos:
		obstaculo.actualizar(delta, lista)
	for guardian in _guardianes:
		guardian.actualizar(delta, lista)
	_programador.actualizar(delta, modificadores)
	_anunciar_tiempo()
	if _estado == Estado.EN_CURSO and _transcurrido >= tiempo_limite:
		_finalizar(ResultadoPartida.MOTIVO_TIEMPO)


## Punto de entrada para todo lo que da puntos. Ignora a quien no puede actuar
## (aturdido o eliminado) y cualquier acción fuera de una partida en curso.
func registrar_puntos(jugador_id: int, fuente: ReglasPartida.FuentePuntos, base: int = -1) -> int:
	if _estado != Estado.EN_CURSO or not _jugadores.has(jugador_id):
		return 0
	if not _jugadores[jugador_id].puede_actuar():
		return 0
	return marcador.sumar(jugador_id, base if base >= 0 else _puntos_por_defecto(fuente), fuente)


## Si alguien se desconecta se conservan sus puntos. Con menos de 2 jugadores la partida termina.
func desconectar_jugador(id: int) -> void:
	_jugadores.erase(id)
	if _estado == Estado.EN_CURSO and _jugadores.size() < ReglasPartida.JUGADORES_MIN:
		_finalizar(ResultadoPartida.MOTIVO_ABANDONO)


# ---- Consultas (las usan el HUD y la arena) ----
func estado() -> Estado:
	return _estado


func jugador(id: int) -> ModeloJugador:
	return _jugadores.get(id)


func jugadores() -> Array:
	return _jugadores.values()


func guardianes() -> Array[Guardian]:
	return _guardianes


func obstaculos() -> Array[Obstaculo]:
	return _obstaculos


func segundos_restantes() -> int:
	return maxi(0, ceili(tiempo_limite - _transcurrido))


## US-026. Solo existe cuando la partida está FINALIZADA; antes devuelve un diccionario vacío.
## Siempre es el mismo resultado: después de finalizar nada puede cambiarlo.
func resultado() -> Dictionary:
	return _resultado.duplicate(true)


## Id del jugador en primer lugar, o -1 si la partida todavía no terminó.
func ganador_id() -> int:
	return _resultado.get("ganadorId", -1)


## Primeros tres lugares (menos si jugaron menos). Vacío si la partida no terminó.
func podio() -> Array:
	return _resultado.get("podio", []).duplicate(true)


func evento_activo() -> EventoEspecial:
	return _programador.evento_activo


## Para forzar un evento (pruebas o demostración).
func lanzar_evento(tipo: FabricaEventos.Tipo) -> void:
	_programador.lanzar(FabricaEventos.crear(tipo), modificadores)


# ---- Internos ----
func _puntos_por_defecto(fuente: ReglasPartida.FuentePuntos) -> int:
	match fuente:
		ReglasPartida.FuentePuntos.REACTOR:
			return ReglasPartida.PUNTOS_REACTOR
		ReglasPartida.FuentePuntos.CELDA:
			return ReglasPartida.PUNTOS_CELDA
		ReglasPartida.FuentePuntos.TERMINAL:
			return ReglasPartida.PUNTOS_TERMINAL
		_:
			return ReglasPartida.PUNTOS_BONIFICACION


func _anunciar_tiempo() -> void:
	var restante := segundos_restantes()
	if restante != _segundo_anunciado:
		_segundo_anunciado = restante
		tiempo_cambiado.emit(restante)


func _al_alcanzar_guardian(guardian_id: int, jugador_id: int, guardian: Guardian) -> void:
	var perdido := -marcador.restar(jugador_id, guardian.penalizacion)
	penalizacion_aplicada.emit(jugador_id, guardian_id, perdido)


func _al_alcanzar_objetivo(_jugador_id: int) -> void:
	_finalizar(ResultadoPartida.MOTIVO_OBJETIVO)


func _finalizar(motivo: String) -> void:
	if _estado == Estado.FINALIZADA:
		return
	_estado = Estado.FINALIZADA
	modificadores.restablecer()
	_resultado = ResultadoPartida.construir(marcador, _cuentas, motivo, _transcurrido, partida_id)
	partida_finalizada.emit(resultado())
