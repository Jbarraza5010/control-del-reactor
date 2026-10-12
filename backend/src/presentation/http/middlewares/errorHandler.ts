import type { ErrorRequestHandler } from 'express';
import { logger } from '../../../shared/logger';

export const errorHandler: ErrorRequestHandler = (err, _req, res, _next) => {
  logger.error('Error no controlado', { message: err instanceof Error ? err.message : String(err) });
  res.status(500).json({ error: { code: 'INTERNAL_ERROR', message: 'Error interno del servidor' } });
};
