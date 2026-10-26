class_name DatoEstadistica
extends ColorRect

@export var titulo: String = "Estadística":
	set(nuevo_titulo):
		titulo = nuevo_titulo
		if is_node_ready():
			$MarginContainer/VBoxContainer/Titulo.text = titulo

@export var valor: String = "0":
	set(nuevo_valor):
		valor = nuevo_valor
		if is_node_ready():
			$MarginContainer/VBoxContainer/Valor.text = valor

func _ready() -> void:
	$MarginContainer/VBoxContainer/Titulo.text = titulo
	$MarginContainer/VBoxContainer/Valor.text = valor

#Para actualizar en código
func actualizar(nuevo_titulo: String, nuevo_valor: Variant) -> void:
	titulo = nuevo_titulo
	valor = str(nuevo_valor)
