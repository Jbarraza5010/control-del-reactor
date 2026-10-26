-- Consulta de lectura para psql; proporcionar -v usuario_id=UUID_AUTENTICADO.
-- En el backend usar un parámetro enlazado equivalente (no concatenar cadenas).
-- El backend debe obtener el ID desde la sesión validada, no confiar en un ID del cliente.
SELECT nombre_usuario,
       partidas_jugadas,
       partidas_ganadas,
       puntos_totales
FROM perfil_estadisticas
WHERE usuario_id = :'usuario_id';
