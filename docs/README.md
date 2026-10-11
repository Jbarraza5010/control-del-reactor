# Documentación

La documentación oficial del proyecto está en la **Wiki de Azure DevOps**. En esta carpeta se versionan los archivos que conviene mantener junto al código, y la Wiki enlaza a ellos.

| Carpeta | Contenido | Plantilla |
|---|---|---|
| `architecture/` | Vistas de arquitectura (lógica, componentes, despliegue) y fuentes editables de los diagramas | [`plantilla-vista.md`](architecture/plantilla-vista.md) |
| `adr/` | Architecture Decision Records: una decisión técnica por archivo | [`0000-plantilla.md`](adr/0000-plantilla.md) |
| `api/` | Contrato de la API REST (endpoints, request, respuestas, errores) | [`plantilla-endpoint.md`](api/plantilla-endpoint.md) |
| `testing/` | Plan de pruebas y casos de prueba por historia de usuario | [`plantilla-plan-de-pruebas.md`](testing/plantilla-plan-de-pruebas.md) · [`plantilla-casos-de-prueba.md`](testing/plantilla-casos-de-prueba.md) |

**Cómo usar las plantillas:** copiar la plantilla, renombrarla (por ejemplo `vista-logica.md`, `0001-stack-backend.md`, `auth.md`, `casos-US-001.md`) y llenarla. Las plantillas se quedan como referencia.
