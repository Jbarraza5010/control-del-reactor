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

# Validar contrasena (Al registrar)
static func validar_contrasena(contrasena: String) -> String:
	# Validar si la contrasena no esta vacia
	if contrasena.is_empty():
		return "La contraseña no puede estar vacia."
	# Validar si la contrasena tiene menos del minimo de caracteres configurado
	if contrasena.length() < CONTRASENA_MIN:
		return "La contraseña debe tener al menos %d caracteres." % CONTRASENA_MIN
	# Validar si la contrasena tiene mas del maximo de caracteres configurado
	if contrasena.length() > CONTRASENA_MAX:
		return "La contraseña no puede superar %d caracteres." % CONTRASENA_MAX
	# Validar si existe una combinacion de letras y numeros
	var tiene_letra := RegEx.create_from_string("[A-Za-z]").search(contrasena) != null
	var tiene_numero := RegEx.create_from_string("[0-9]").search(contrasena) != null
	if not (tiene_letra and tiene_numero):
		return "La contraseña debe incluir al menos una letra y un número."
	return ""

# Validación del login
static func validar_login(correo: String, contrasena: String) -> String:
	# Validar si el campo de correo o contrasena no estan vacios
	if correo.is_empty() or contrasena.is_empty():
		return "Ingrese su correo y contraseña."
	return ""
	
# Validación de código de un solo uso:
static func validar_codigo(codigo: String) -> String:
	if codigo.is_empty():
		return "Ingrese el código de un solo uso"
	return ""
