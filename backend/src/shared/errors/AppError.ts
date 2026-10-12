/**
 * Jerarquía de errores de la aplicación.
 * Las capas internas lanzan estos errores; solo el middleware HTTP los traduce a respuestas.
 */
export class AppError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly httpStatus: number,
    public readonly details?: unknown,
  ) {
    super(message);
    this.name = new.target.name;
  }
}

export class ValidationError extends AppError {
  constructor(message = 'Datos de entrada inválidos', details?: unknown) {
    super('VALIDATION_ERROR', message, 400, details);
  }
}

export class UnauthorizedError extends AppError {
  constructor(message = 'Credenciales inválidas') {
    super('UNAUTHORIZED', message, 401);
  }
}

export class ForbiddenError extends AppError {
  constructor(message = 'Acción no permitida') {
    super('FORBIDDEN', message, 403);
  }
}

export class NotFoundError extends AppError {
  constructor(message = 'Recurso no encontrado') {
    super('NOT_FOUND', message, 404);
  }
}

export class ConflictError extends AppError {
  constructor(message = 'El recurso ya existe') {
    super('CONFLICT', message, 409);
  }
}

export class NotImplementedError extends AppError {
  constructor(message = 'Endpoint pendiente de implementar') {
    super('NOT_IMPLEMENTED', message, 501);
  }
}
