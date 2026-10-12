# ADR-004 — Patrones Repository, Factory y Observer en el Sprint 2

**Estado:** Aceptada · **Responsable:** Ulfrán Rodríguez

## Contexto
La ERS (sección 7.3) propone cinco patrones: Factory Method, Repository, Strategy, Observer y State.
En el Sprint 2 el backend solo cubre cuentas; Strategy y State pertenecen al motor de partida (guardianes y estados del jugador).

## Decisión
Se aplican tres patrones donde resuelven un problema real del Sprint 2:

| Patrón | Implementación | Problema que resuelve |
|--------|----------------|-----------------------|
| Repository | `UserRepository` (interfaz) con `PrismaUserRepository` e `InMemoryUserRepository` | Desacopla el dominio de PostgreSQL y permite pruebas sin base de datos |
| Factory | `MailerFactory.create(env)` | Elige `ConsoleMailer` (desarrollo) o `SmtpMailer` (producción) sin que el resto del código lo sepa |
| Observer | `EventBus` con `registerMailListeners` | Registrar un usuario publica `UserRegistered`; el envío del correo reacciona sin acoplarse al servicio |

Además se usa inyección de dependencias manual en `src/container.ts`.

## Alternativas consideradas
- Aplicar Strategy y State ahora: se descartó porque no hay aún comportamiento que justifique sustituir (guardianes, estados de jugador); sería sobreingeniería.
- Librería de inyección de dependencias (tsyringe, Inversify): agrega decoradores y configuración que no se justifican con este tamaño.

## Consecuencias
- (+) Cada patrón tiene pruebas (`userRepository`, `mailerFactory`, `eventBus`).
- (+) El `EventBus` se reutilizará en el Sprint 3-4 para propagar puntajes y ranking (Observer en la ERS).
- (−) El bus es en memoria, dentro de un solo proceso. Si el backend se escala a varias instancias habrá que reemplazarlo por un broker.
