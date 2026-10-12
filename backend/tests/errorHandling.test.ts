import express from 'express';
import request from 'supertest';
import { describe, expect, it } from 'vitest';
import { z } from 'zod';
import { asyncHandler } from '../src/presentation/http/asyncHandler';
import { errorHandler } from '../src/presentation/http/middlewares/errorHandler';
import { createApp } from '../src/presentation/http/app';
import { ConflictError, NotImplementedError } from '../src/shared/errors/AppError';

function appWith(setup: (app: express.Express) => void) {
  const app = express();
  app.use(express.json());
  setup(app);
  app.use(errorHandler);
  return app;
}

describe('manejo de errores', () => {
  it('AppError se traduce a su código HTTP y formato uniforme', async () => {
    const app = appWith((a) => a.get('/x', () => { throw new ConflictError('correo duplicado'); }));
    const res = await request(app).get('/x');
    expect(res.status).toBe(409);
    expect(res.body.error).toMatchObject({ code: 'CONFLICT', message: 'correo duplicado' });
  });

  it('errores async llegan al handler mediante asyncHandler', async () => {
    const app = appWith((a) =>
      a.get('/x', asyncHandler(async () => { throw new NotImplementedError(); })),
    );
    const res = await request(app).get('/x');
    expect(res.status).toBe(501);
  });

  it('ZodError se traduce a 400 VALIDATION_ERROR', async () => {
    const app = appWith((a) =>
      a.post('/x', (req) => { z.object({ email: z.string().email() }).parse(req.body); }),
    );
    const res = await request(app).post('/x').send({ email: 'no-es-correo' });
    expect(res.status).toBe(400);
    expect(res.body.error.code).toBe('VALIDATION_ERROR');
  });

  it('error inesperado devuelve 500 sin filtrar detalles internos', async () => {
    const app = appWith((a) => a.get('/x', () => { throw new Error('secreto interno'); }));
    const res = await request(app).get('/x');
    expect(res.status).toBe(500);
    expect(JSON.stringify(res.body)).not.toContain('secreto interno');
  });

  it('JSON malformado devuelve 400', async () => {
    const app = createApp({ database: { ping: async () => undefined } });
    const res = await request(app).post('/api/v1/auth/register').set('Content-Type', 'application/json').send('{mal');
    expect(res.status).toBe(400);
    expect(res.body.error.code).toBe('VALIDATION_ERROR');
  });

  it('endpoints de auth pendientes responden 501', async () => {
    const app = createApp({ database: { ping: async () => undefined } });
    const res = await request(app).post('/api/v1/auth/login').send({});
    expect(res.status).toBe(501);
    expect(res.body.error.code).toBe('NOT_IMPLEMENTED');
  });
});
