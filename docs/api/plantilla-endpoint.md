# API — <Módulo> (ej. Autenticación)

> Copiar este archivo por módulo (por ejemplo `auth.md`, `perfil.md`, `hardware.md`) y repetir la sección de endpoint por cada uno.
> Si el equipo genera un `openapi.yaml`, este documento puede resumirlo y enlazarlo.

- **URL base:** `http://localhost:8080/api`
- **Formato:** JSON
- **Autenticación:** `Authorization: Bearer <token>` (salvo que se indique lo contrario)
- **Responsable:**

## Resumen de endpoints

| Método | Ruta | Descripción | Requiere token | Historia |
|---|---|---|---|---|
| POST | `/auth/register` | Registrar cuenta | No | US-001 |
| | | | | |

---

## `MÉTODO /ruta`

**Descripción:** qué hace el endpoint.
**Historia de usuario:** US-XXX · **Caso de uso:** UC-XX

### Request

| Campo | Tipo | Obligatorio | Reglas |
|---|---|---|---|
| `campo` | string | Sí | Ej. formato de correo válido |

```json
{
  "campo": "valor"
}
```

### Respuestas

| Código | Cuándo | Cuerpo |
|---|---|---|
| `201` | Éxito | Ver ejemplo |
| `400` | Datos inválidos | Error estándar |
| `409` | Conflicto (ej. correo ya registrado) | Error estándar |

```json
{
  "id": "…"
}
```

---

## Formato estándar de error

```json
{
  "error": {
    "code": "EMAIL_ALREADY_EXISTS",
    "message": "El correo ya está registrado."
  }
}
```

| Código de error | HTTP | Significado |
|---|---|---|
| `VALIDATION_ERROR` | 400 | Algún campo no cumple las reglas |
| `UNAUTHORIZED` | 401 | Token ausente, inválido o expirado |
| | | |
