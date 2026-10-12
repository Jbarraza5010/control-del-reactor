import request from 'supertest';
import { describe, expect, it } from 'vitest';
import type { DatabaseHealth } from '../src/application/ports/DatabaseHealth';
import { createApp } from '../src/presentation/http/app';

const dbUp: DatabaseHealth = { ping: async () => undefined };
const dbDown: DatabaseHealth = {
  ping: async () => {
    throw new Error('sin conexión');
  },
};

describe('esqueleto HTTP', () => {
  it('GET /health responde ok', async () => {
    const res = await request(createApp({ database: dbUp })).get('/health');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
  });

  it('GET /health/db responde 200 si la BD responde y 503 si no', async () => {
    const up = await request(createApp({ database: dbUp })).get('/health/db');
    expect(up.status).toBe(200);
    expect(up.body.database).toBe('up');

    const down = await request(createApp({ database: dbDown })).get('/health/db');
    expect(down.status).toBe(503);
    expect(down.body.database).toBe('down');
  });

  it('ruta inexistente responde 404 con formato de error', async () => {
    const res = await request(createApp({ database: dbUp })).get('/nada');
    expect(res.status).toBe(404);
    expect(res.body.error.code).toBe('NOT_FOUND');
  });
});
