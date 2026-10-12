# ADR-006 — Manejo de errores centralizado con AppError

**Estado:** Aceptada · **Responsable:** Ulfrán Rodríguez

## Contexto
La DoD exige manejo adecuado de errores. Los casos de uso de la ERS definen excepciones precisas
(por ejemplo, UC-03 E1: mensaje genérico idéntico si el usuario no existe o la contraseña es incorrecta).

## Decisión
- Las capas internas lanzan subclases de `AppError` (`ValidationError` 400, `UnauthorizedError` 401, `ForbiddenError` 403, `NotFoundError` 404, `ConflictError` 409, `NotImplementedError` 501), cada una con un `code` estable.
- El middleware `errorHandler` es el único que convierte errores en respuestas HTTP con formato uniforme `{ "error": { "code", "message", "details?" } }`.
- Los errores de validación de zod y el JSON malformado se traducen a 400.
- Un error inesperado devuelve 500 genérico; el detalle y el stack solo se escriben en el log.
- Los handlers `async` usan `asyncHandler` porque Express 4 no propaga sus rechazos.

## Alternativas consideradas
- `try/catch` en cada controlador: duplica código y facilita respuestas inconsistentes.
- Devolver objetos Result en lugar de lanzar excepciones: más explícito, pero más verboso para el tamaño del equipo.

## Consecuencias
- (+) Los clientes (Godot) reciben siempre el mismo formato y pueden decidir por `code`.
- (+) Nunca se filtran detalles internos al cliente.
- (−) Quien implemente un caso de uso debe elegir el `AppError` correcto; se revisa en los Pull Requests.
