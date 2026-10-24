class_name ValidacionCuenta
extends RefCounted

# REGLAS DE VALIDACION
# Cantidad mínima de caracteres en nombre de usuario
const USUARIO_MIN := 3
# Cantidad máxima de caracteres en nombre de usuario
const USUARIO_MAX := 20
# Cantidad mínima de caracteres en contraseña
const CONTRASENA_MIN := 8
# Cantidad máxima de caracteres
const CONTRASENA_MAX := 64

# Validar nombre de usuario (Al registrar)
static func validar_usuario(usuario: String) -> String:
	# Validar si el nombre de usuario no esta vacio
	if usuario.is_empty():
		return "El nombre de usuario no puede estar vacio."
	# Validar si el nombre de usuario contiene el minimo y el maximo configurado
	if usuario.length() < USUARIO_MIN or usuario.length() > USUARIO_MAX:
		return "El nombre de usuario debe tener entre %d y %d caracteres." % [USUARIO_MIN, USUARIO_MAX]
	# Filtro de texto para el usuario
	var regex := RegEx.new()
	# Letras A a la Z minuscula o mayuscula, numeros de 0 a 9 y "_"
	regex.compile("^[A-Za-z0-9_]+$")
	if regex.search(usuario) == null:
		return "El usuario solo puede tener letras, números y guion bajo (_)."
	return ""

# Validar correo (Al registrar)
static func validar_correo(correo: String) -> String:
	# Validar si el correo no esta vacio
	if correo.is_empty():
		return "El correo no puede estar vacio."
	# 
	var regex := RegEx.new()
	# Formato de filtro para correos electronicos
	regex.compile("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
	if regex.search(correo) == null:
		return "El correo tiene un formato inválido."
	return ""
