# Backend — Control del Reactor (Sprint 2)

API REST de cuentas: Node.js 20 + TypeScript + Express, Prisma + PostgreSQL.

## Arquitectura por capas

```
src/
├── config/            Variables de entorno validadas
├── presentation/http/ Express: rutas, controladores, middlewares (HTTP aquí y solo aquí)
├── application/       Casos de uso (servicios) y puertos (interfaces hacia afuera)
├── domain/            Entidades y contratos de repositorio. TypeScript puro
├── infrastructure/    Implementaciones: Prisma, correo
└── shared/            Logger, errores, eventos
```

Regla de dependencia: `presentation -> application -> domain` y `infrastructure -> domain/application`.
El dominio no importa nada de Express ni de Prisma.

## Patrones de diseño aplicados

| Patrón | Dónde | Para qué |
|--------|-------|----------|
| Repository | `domain/repositories/UserRepository` + `infrastructure/persistence/{prisma,memory}` | El dominio no conoce PostgreSQL; las pruebas usan la versión en memoria |
| Factory | `infrastructure/mail/MailerFactory` | Elige ConsoleMailer o SmtpMailer según `MAIL_TRANSPORT` |
| Observer | `shared/events/EventBus` + `application/services/registerMailListeners` | Registrar un usuario dispara el correo sin acoplar ambos |
| Inyección de dependencias | `src/container.ts` (composition root) | Único lugar que elige implementaciones concretas |

## Manejo de errores

Las capas internas lanzan subclases de `AppError` (`ValidationError`, `ConflictError`, `UnauthorizedError`, `NotFoundError`...).
`presentation/http/middlewares/errorHandler.ts` las convierte en `{ "error": { "code", "message", "details?" } }`.
Un error inesperado devuelve 500 genérico y el detalle solo queda en el log.
En handlers `async` se usa `asyncHandler(...)`.

## Comandos

```
npm install
npm run dev        # desarrollo con recarga
npm test           # pruebas
npm run typecheck  # genera el cliente Prisma y compila sin emitir
```
