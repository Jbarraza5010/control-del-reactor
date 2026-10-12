import type { PrismaClient, Usuario } from '@prisma/client';
import type { User, UserStatus } from '../../../domain/entities/User';
import type { UserRepository } from '../../../domain/repositories/UserRepository';

/** Implementación de UserRepository sobre PostgreSQL mediante Prisma. */
export class PrismaUserRepository implements UserRepository {
  constructor(private readonly prisma: PrismaClient) {}

  async findById(id: string): Promise<User | null> {
    const row = await this.prisma.usuario.findUnique({ where: { id } });
    return row ? toDomain(row) : null;
  }

  async findByEmail(email: string): Promise<User | null> {
    const row = await this.prisma.usuario.findUnique({ where: { email: email.toLowerCase() } });
    return row ? toDomain(row) : null;
  }

  async findByUsername(username: string): Promise<User | null> {
    const row = await this.prisma.usuario.findUnique({ where: { username } });
    return row ? toDomain(row) : null;
  }

  async save(user: User): Promise<User> {
    const data = {
      username: user.username,
      email: user.email.toLowerCase(),
      passwordHash: user.passwordHash,
      status: user.status,
    };
    const row = await this.prisma.usuario.upsert({
      where: { id: user.id },
      create: { id: user.id, ...data },
      update: data,
    });
    return toDomain(row);
  }
}

function toDomain(row: Usuario): User {
  return {
    id: row.id,
    username: row.username,
    email: row.email,
    passwordHash: row.passwordHash,
    status: row.status as UserStatus,
    createdAt: row.createdAt,
  };
}
