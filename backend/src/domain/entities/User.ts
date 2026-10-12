/**
 * Entidad de dominio "Usuario" (ERS sección 6: Usuario).
 * Es TypeScript puro: no depende de Express ni de Prisma.
 */
export type UserStatus = 'PENDIENTE_VERIFICACION' | 'ACTIVA';

export interface User {
  id: string;
  username: string;
  email: string;
  passwordHash: string;
  status: UserStatus;
  createdAt: Date;
}
