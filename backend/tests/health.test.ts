import request from 'supertest';
import { describe, expect, it } from 'vitest';
import { createApp } from '../src/presentation/http/app';

describe('esqueleto HTTP', () => {
  const app = createApp();

  it('GET /health responde ok', async () => {
    const res = await request(app).get('/health');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
  });

  it('endpoints de auth pendientes responden 501', async () => {
    const res = await request(app).post('/api/v1/auth/register').send({});
    expect(res.status).toBe(501);
    expect(res.body.error.code).toBe('NOT_IMPLEMENTED');
  });

  it('ruta inexistente responde 404 con formato de error', async () => {
    const res = await request(app).get('/nada');
    expect(res.status).toBe(404);
    expect(res.body.error.code).toBe('NOT_FOUND');
  });
});
