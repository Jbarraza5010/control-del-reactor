import type { User } from '../entities/User';
import type { Repository } from './Repository';

/**
 * Puerto de persistencia de usuarios. El dominio y los servicios dependen de ESTA interfaz;
 * no saben si detrás hay Prisma/PostgreSQL o una lista en memoria (pruebas).
 */
export interface UserRepository extends Repository<User, string> {
  findByEmail(email: string): Promise<User | null>;
  findByUsername(username: string): Promise<User | null>;
}
