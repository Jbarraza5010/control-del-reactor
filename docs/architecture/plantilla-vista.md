# Vista de arquitectura: <Nombre de la vista>

> Copiar este archivo por cada vista (por ejemplo `vista-logica.md`, `vista-componentes.md`, `vista-despliegue.md`).
> Guardar el archivo editable del diagrama (`.drawio`, `.puml`) en esta misma carpeta y la imagen exportada (`.png`/`.svg`) junto a él.

- **Tipo de vista:** Lógica | Componentes | Despliegue | Secuencia
- **Versión / Sprint:** Sprint 2
- **Autor(es):**
- **Última actualización:** AAAA-MM-DD

## 1. Propósito

¿Qué muestra esta vista y a quién le sirve?

## 2. Diagrama

![Diagrama](./nombre-del-diagrama.png)

Archivo editable: [`nombre-del-diagrama.drawio`](./nombre-del-diagrama.drawio)

## 3. Elementos

| Elemento | Tipo | Responsabilidad | Tecnología |
|---|---|---|---|
| Ej. Servicio de Autenticación | Componente | Registro, login, verificación de correo | <stack> |
| | | | |

## 4. Relaciones y comunicación

| Origen | Destino | Protocolo / mecanismo | Descripción |
|---|---|---|---|
| Ej. Cliente Godot | API REST | HTTP/JSON | Operaciones de cuenta y perfil |
| | | | |

## 5. Patrones aplicados

| Patrón | Tipo | Dónde se aplica (carpeta / clase) | Requisito que lo justifica |
|---|---|---|---|
| Ej. Repository | Estructural | `backend/src/infrastructure/persistence/` | RNF de mantenibilidad, persistencia en PostgreSQL |
| | | | |

## 6. Decisiones relacionadas

- [ADR-0001: …](../adr/0001-....md)

## 7. Cambios respecto a la versión anterior

- Ej. Se agregó el puente serial entre el Arduino y el backend.
