import { Router, type RequestHandler } from 'express';
import { NotImplementedError } from '../../../shared/errors/AppError';

/**
 * Contrato inicial de la API de cuentas (Sprint 2).
 * Todos los endpoints responden 501 hasta que Moisés los implemente:
 *   US-001/002/003 -> register    US-004 -> verify-email
 *   US-005 -> login               US-007 -> forgot-password / reset-password
 * Al implementarlos: validar con zod, llamar a un servicio de application/ y lanzar AppError.
 */
const pendiente: RequestHandler = () => {
  throw new NotImplementedError();
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
