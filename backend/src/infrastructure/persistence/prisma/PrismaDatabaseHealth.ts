import type { PrismaClient } from '@prisma/client';
import type { DatabaseHealth } from '../../../application/ports/DatabaseHealth';

export class PrismaDatabaseHealth implements DatabaseHealth {
  constructor(private readonly prisma: PrismaClient) {}

  async ping(): Promise<void> {
    await this.prisma.$queryRaw`SELECT 1`;
  }
}
