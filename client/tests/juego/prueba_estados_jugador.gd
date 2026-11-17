extends CasoPrueba
## Patrón State: transiciones del jugador (US de estados del jugador).


func _jugador() -> ModeloJugador:
	return ModeloJugador.new(1, "Ana", Vector2(10, 10))


func test_jugador_nuevo_esta_normal_y_se_mueve() -> void:
	var j := _jugador()
	afirmar_igual(j.nombre_estado(), "normal", "estado inicial")
	afirmar(j.puede_moverse(), "un jugador normal se mueve")
	afirmar_igual(j.velocidad_actual(), ReglasPartida.VELOCIDAD_BASE, "velocidad normal")


func test_golpe_aturde_y_detiene() -> void:
	var j := _jugador()
	afirmar(j.recibir_golpe(), "el golpe tiene efecto")
	afirmar_igual(j.nombre_estado(), "aturdido", "pasa a aturdido")
	afirmar(not j.puede_moverse(), "aturdido no se mueve")
	afirmar(not j.puede_actuar(), "aturdido no actúa")
	afirmar_igual(j.velocidad_actual(), 0.0, "velocidad 0")


func test_aturdido_no_recibe_otro_golpe_y_se_recupera() -> void:
	var j := _jugador()
	j.recibir_golpe()
	afirmar(not j.recibir_golpe(), "no recibe golpe mientras está aturdido")
	afirmar_igual(j.golpes, 1, "solo cuenta un golpe")
	avanzar(j, ReglasPartida.ATURDIMIENTO_S + 0.2)
	afirmar_igual(j.nombre_estado(), "normal", "vuelve a normal")


func test_tercer_golpe_elimina_y_reaparece_en_el_inicio() -> void:
	var j := _jugador()
	j.posicion = Vector2(500, 500)
	for i in ReglasPartida.GOLPES_PARA_ELIMINAR:
		j.recibir_golpe()
		avanzar(j, ReglasPartida.ATURDIMIENTO_S + 0.2) if i < ReglasPartida.GOLPES_PARA_ELIMINAR - 1 else null
	afirmar_igual(j.nombre_estado(), "eliminado", "tercer golpe elimina")
	afirmar_igual(j.posicion, Vector2(10, 10), "regresa al punto de inicio")
	avanzar(j, ReglasPartida.REAPARICION_S + 0.2)
	afirmar_igual(j.nombre_estado(), "normal", "reaparece normal")
	afirmar_igual(j.golpes, 0, "recupera sus golpes")


func test_escudo_bloquea_golpes_y_expira() -> void:
	var j := _jugador()
	afirmar(j.activar_escudo(), "se activa el escudo")
	afirmar(j.puede_moverse(), "escudado se mueve")
	afirmar(not j.recibir_golpe(), "escudado no recibe golpes")
	avanzar(j, ReglasPartida.ESCUDO_S + 0.2)
	afirmar_igual(j.nombre_estado(), "normal", "el escudo expira")


func test_no_se_activa_escudo_estando_aturdido() -> void:
	var j := _jugador()
	j.recibir_golpe()
	afirmar(not j.activar_escudo(), "no hay escudo si está aturdido")
