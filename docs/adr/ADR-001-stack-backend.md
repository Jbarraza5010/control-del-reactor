# ADR-001 — Backend con Node.js 20 + TypeScript + Express

**Estado:** Aceptada · **Responsable:** Ulfrán Rodríguez

## Contexto
La ERS (sección 7.4) permite elegir el backend entre GDScript, Node.js (NestJS) o .NET (ASP.NET Core).
El Sprint 2 exige cuentas (registro, verificación de correo, inicio de sesión, recuperación) sobre PostgreSQL,
con Docker y CI. El equipo ya trabaja con JavaScript/TypeScript y el cliente Godot solo necesita consumir HTTP/JSON.

## Decisión
Node.js 20 LTS con TypeScript (modo estricto) y Express 4.

## Alternativas consideradas
- **NestJS:** trae estructura propia, pero agrega curva de aprendizaje y mucho código base para un backend pequeño.
- **ASP.NET Core:** sólido, pero ningún integrante lo domina y la imagen Docker es más pesada.
- **GDScript como backend:** mantendría un solo lenguaje con el cliente, pero no tiene ecosistema maduro para autenticación, correo, ORM ni pruebas.

## Consecuencias
- (+) Un lenguaje tipado con ecosistema amplio (zod, Prisma, vitest, supertest, nodemailer).
- (+) Express es mínimo: la estructura la define nuestra arquitectura por capas (ADR-002), no el framework.
- (−) Express no impone orden; hay que mantener la disciplina de capas con revisión de Pull Requests.
