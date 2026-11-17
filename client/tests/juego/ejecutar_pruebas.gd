extends SceneTree
## Ejecuta todas las pruebas de client/tests/juego/ (archivos prueba_*.gd).
##
## Desde la raíz del repositorio:
##   godot --headless --path client -s res://tests/juego/ejecutar_pruebas.gd
## Termina con código 0 si todo pasó y 1 si algo falló (sirve para el pipeline de CI).

const CARPETA := "res://tests/juego/"


func _initialize() -> void:
	var total_pruebas := 0
	var total_fallas := 0
	var archivos := DirAccess.get_files_at(CARPETA)
	archivos.sort()
	for archivo in archivos:
		if not (archivo.begins_with("prueba_") and archivo.ends_with(".gd")):
			continue
		var script: GDScript = load(CARPETA + archivo)
		print("\n== %s ==" % archivo)
		if script == null or not script.can_instantiate():
			# Si un archivo no compila, cuenta como fallo (antes se ignoraba en silencio).
			total_fallas += 1
			print("  FALLÓ no se pudo cargar el archivo (revisar errores de sintaxis)")
			continue
		for metodo in script.get_script_method_list():
			if not metodo["name"].begins_with("test_"):
				continue
			var caso: CasoPrueba = script.new()
			caso.call(metodo["name"])
			total_pruebas += 1
			if caso.fallos.is_empty():
				print("  OK    %s (%d verificaciones)" % [metodo["name"], caso.afirmaciones])
			else:
				total_fallas += 1
				print("  FALLÓ %s" % metodo["name"])
				for f in caso.fallos:
					print("        - %s" % f)
	print("\nResumen: %d pruebas, %d fallidas" % [total_pruebas, total_fallas])
	quit(1 if total_fallas > 0 else 0)
