import { PrismaClient } from '@prisma/client';

/** Una sola instancia de PrismaClient para todo el proceso. */
let client: PrismaClient | undefined;

export function getPrismaClient(): PrismaClient {
  client ??= new PrismaClient();
  return client;
}

export async function disconnectPrisma(): Promise<void> {
  await client?.$disconnect();
  client = undefined;
}
