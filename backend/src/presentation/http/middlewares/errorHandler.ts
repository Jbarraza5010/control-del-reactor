import type { ErrorRequestHandler } from 'express';
import { ZodError } from 'zod';
import { AppError, ValidationError } from '../../../shared/errors/AppError';
import { logger } from '../../../shared/logger';

/**
 * Único punto donde un error se convierte en respuesta HTTP.
 * Formato uniforme: { error: { code, message, details? } }
 */
export const errorHandler: ErrorRequestHandler = (err, _req, res, _next) => {
  let appError: AppError | undefined;

  if (err instanceof AppError) appError = err;
  else if (err instanceof ZodError) appError = new ValidationError('Datos de entrada inválidos', err.flatten());
  else if (err && (err as { type?: string }).type === 'entity.parse.failed') {
    appError = new ValidationError('El cuerpo de la petición no es JSON válido');
  }

  if (appError) {
    res.status(appError.httpStatus).json({
      error: { code: appError.code, message: appError.message, details: appError.details },
    });
    return;
  }

  // Error inesperado: se registra completo, pero al cliente solo se le da un mensaje genérico.
  logger.error('Error no controlado', {
    message: err instanceof Error ? err.message : String(err),
    stack: err instanceof Error ? err.stack : undefined,
  });
  res.status(500).json({ error: { code: 'INTERNAL_ERROR', message: 'Error interno del servidor' } });
};
