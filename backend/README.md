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

## Comandos

```
npm install
npm run dev        # desarrollo con recarga
npm test           # pruebas
npm run typecheck
```
