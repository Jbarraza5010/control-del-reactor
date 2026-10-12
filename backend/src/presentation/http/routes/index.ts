import { Router } from 'express';
import { authRoutes } from './auth.routes';
import { healthRoutes } from './health.routes';

export function buildRouter(): Router {
  const router = Router();
  router.use('/health', healthRoutes());
  router.use('/api/v1/auth', authRoutes());
  return router;
}
