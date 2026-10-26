# Plan de pruebas — Sprint <N>

- **Responsable:**
- **Versión:** 1.0
- **Fecha:** AAAA-MM-DD

## 1. Objetivo

Qué se busca verificar en este Sprint.

## 2. Alcance

**Se prueba:**

| Historia | Descripción |
|---|---|
| US-001 | Registro de cuenta |
| | |

**No se prueba en este Sprint:** (y por qué)

## 3. Niveles de prueba

| Nivel | Qué cubre | Herramienta | Automatizada en CI |
|---|---|---|---|
| Unitarias | Dominio y servicios del backend | <framework> | Sí |
| Integración | API + PostgreSQL en contenedor | <framework> | Sí |
| Aceptación | Criterios de aceptación de cada historia | Manual / <herramienta> | Parcial |
| Hardware | Arduino / simulador → backend → cliente | Manual | No |

## 4. Entorno de pruebas

- `docker compose up` con la base de datos de pruebas
- Simulador del panel o Arduino físico
- Versión / commit probado:

## 5. Criterios

- **De entrada:** la historia está implementada y su PR pasó el CI.
- **De salida:** todos los casos de prioridad alta pasan y no hay bugs críticos abiertos.
- **Cobertura mínima:** 70 % en la lógica de dominio (según el DoD).

## 6. Escenarios de prueba

| ID | Escenario | Historia |
|---|---|---|
| ESC-01 | Registro exitoso de usuario | US-001 |
| ESC-02 | Intento de registro con correo duplicado | US-002 |
| ESC-03 | Inicio de sesión correcto | US-005 |
| | | |

## 7. Riesgos de pruebas

| Riesgo | Mitigación |
|---|---|
| El Arduino no está disponible para probar | Se prueba con el simulador y se registra la evidencia |
| | |
