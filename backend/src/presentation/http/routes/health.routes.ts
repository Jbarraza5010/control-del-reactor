import { Router } from 'express';

export function healthRoutes(): Router {
  const router = Router();

  // Liveness: el proceso está vivo. Lo usa Docker (HEALTHCHECK) y el CI.
  router.get('/', (_req, res) => {
    res.json({ status: 'ok', uptime: process.uptime(), timestamp: new Date().toISOString() });
  });

  return router;
}
