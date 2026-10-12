import { Router } from 'express';
import type { DatabaseHealth } from '../../../application/ports/DatabaseHealth';
import { authRoutes } from './auth.routes';
import { healthRoutes } from './health.routes';

export interface RouterDeps {
  database: DatabaseHealth;
}

export function buildRouter(deps: RouterDeps): Router {
  const router = Router();
  router.use('/health', healthRoutes(deps.database));
  router.use('/api/v1/auth', authRoutes());
  return router;
}
