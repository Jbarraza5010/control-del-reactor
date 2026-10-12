import type { User } from '../../../domain/entities/User';
import type { UserRepository } from '../../../domain/repositories/UserRepository';

/** Implementación en memoria: permite probar la lógica sin base de datos. */
export class InMemoryUserRepository implements UserRepository {
  private readonly users = new Map<string, User>();

  async findById(id: string): Promise<User | null> {
    return this.users.get(id) ?? null;
  }

  async findByEmail(email: string): Promise<User | null> {
    const target = email.toLowerCase();
    return [...this.users.values()].find((u) => u.email.toLowerCase() === target) ?? null;
  }

  async findByUsername(username: string): Promise<User | null> {
    const target = username.toLowerCase();
    return [...this.users.values()].find((u) => u.username.toLowerCase() === target) ?? null;
  }

  async save(user: User): Promise<User> {
    this.users.set(user.id, user);
    return user;
  }
}
