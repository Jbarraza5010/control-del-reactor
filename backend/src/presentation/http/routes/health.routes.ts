import { Router } from 'express';
import type { DatabaseHealth } from '../../../application/ports/DatabaseHealth';
import { asyncHandler } from '../asyncHandler';

export function healthRoutes(database: DatabaseHealth): Router {
  const router = Router();

  // Liveness: el proceso está vivo. Lo usa Docker (HEALTHCHECK) y el CI.
  router.get('/', (_req, res) => {
    res.json({ status: 'ok', uptime: process.uptime(), timestamp: new Date().toISOString() });
  });

  // Readiness: además verifica la conexión con PostgreSQL.
  router.get(
    '/db',
    asyncHandler(async (_req, res) => {
      try {
        await database.ping();
        res.json({ status: 'ok', database: 'up' });
      } catch {
        res.status(503).json({ status: 'degraded', database: 'down' });
      }
    }),
  );

  return router;
}
