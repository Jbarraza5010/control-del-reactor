import { Router, type RequestHandler } from 'express';

/**
 * Contrato inicial de la API de cuentas (Sprint 2).
 * Todos los endpoints responden 501 hasta que Moisés los implemente:
 *   US-001/002/003 -> register    US-004 -> verify-email
 *   US-005 -> login               US-007 -> forgot-password / reset-password
 */
const pendiente: RequestHandler = (_req, res) => {
  res.status(501).json({ error: { code: 'NOT_IMPLEMENTED', message: 'Endpoint pendiente de implementar' } });
};

export function authRoutes(): Router {
  const router = Router();
  router.post('/register', pendiente);
  router.post('/verify-email', pendiente);
  router.post('/login', pendiente);
  router.post('/forgot-password', pendiente);
  router.post('/reset-password', pendiente);
  return router;
}
