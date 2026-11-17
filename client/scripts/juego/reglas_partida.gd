class_name ReglasPartida
extends RefCounted
## Reglas del juego en un solo lugar (ERS: reglas de negocio). Si hay que balancear
## el juego, se cambia aquí y no en cada clase.

## De dónde viene cada punto (el marcador usa esto para aplicar multiplicadores).
enum FuentePuntos { REACTOR, CELDA, TERMINAL, BONIFICACION, EVENTO }

# ---- Partida ----
const JUGADORES_MIN := 2
const JUGADORES_MAX := 4
const TIEMPO_LIMITE_S := 300.0  # 5 minutos (infografía del enunciado)
const PUNTUACION_OBJETIVO := 1000

# ---- Puntos base por acción (infografía del enunciado) ----
const PUNTOS_REACTOR := 20  # por cada ciclo de extracción completado
const PUNTOS_CELDA := 10
const PUNTOS_TERMINAL := 25
const PUNTOS_BONIFICACION := 15

# ---- Jugador ----
const VELOCIDAD_BASE := 100.0  # mismo valor que jugador.gd
const GOLPES_PARA_ELIMINAR := 3
const ATURDIMIENTO_S := 2.0
const ESCUDO_S := 5.0
const REAPARICION_S := 3.0

# ---- Guardianes ----
const PENALIZACION_GUARDIAN := 15  # energía (puntos) que pierde el jugador alcanzado
const VELOCIDAD_PATRULLERO := 60.0
const VELOCIDAD_PERSEGUIDOR := 80.0
const RADIO_CONTACTO := 14.0
const RADIO_DETECCION := 160.0

# ---- Obstáculos ----
const FACTOR_TRAMPA := 0.5  # la trampa reduce la velocidad a la mitad
const PUERTA_ABIERTA_S := 3.0
const PUERTA_RADIO_ACTIVACION := 48.0

# ---- Eventos especiales ----
const INTERVALO_EVENTOS_MIN_S := 20.0
const INTERVALO_EVENTOS_MAX_S := 40.0
const SOBRECARGA_DURACION_S := 15.0
const SOBRECARGA_FACTOR := 2.0
const MULTIPLICADOR_DURACION_S := 10.0
const MULTIPLICADOR_FACTOR := 2.0
const CELDAS_EXTRA := 5
