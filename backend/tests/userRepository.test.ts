import { describe, expect, it } from 'vitest';
import type { User } from '../src/domain/entities/User';
import { InMemoryUserRepository } from '../src/infrastructure/persistence/memory/InMemoryUserRepository';

const user: User = {
  id: '1', username: 'Ulfran', email: 'Ulfran@tec.ac.cr', passwordHash: 'hash',
  status: 'PENDIENTE_VERIFICACION', createdAt: new Date(),
};

describe('UserRepository (Repository, versión en memoria)', () => {
  it('guarda y recupera por id, correo y usuario sin distinguir mayúsculas', async () => {
    const repo = new InMemoryUserRepository();
    await repo.save(user);
    expect(await repo.findById('1')).toEqual(user);
    expect(await repo.findByEmail('ulfran@TEC.ac.cr')).toEqual(user);
    expect(await repo.findByUsername('ULFRAN')).toEqual(user);
  });

  it('devuelve null cuando no existe', async () => {
    const repo = new InMemoryUserRepository();
    expect(await repo.findById('x')).toBeNull();
  });
});
