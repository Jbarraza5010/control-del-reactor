import { registerMailListeners } from './application/services/registerMailListeners';
import type { Env } from './config/env';
import { MailerFactory } from './infrastructure/mail/MailerFactory';
import { getPrismaClient } from './infrastructure/persistence/prisma/PrismaClientProvider';
import { PrismaDatabaseHealth } from './infrastructure/persistence/prisma/PrismaDatabaseHealth';
import { PrismaUserRepository } from './infrastructure/persistence/prisma/PrismaUserRepository';
import { EventBus } from './shared/events/EventBus';

/**
 * Composition root: el ÚNICO lugar donde se eligen las implementaciones concretas
 * y se conectan entre sí (inyección de dependencias manual, sin librerías).
 */
export function buildContainer(env: Env) {
  const prisma = getPrismaClient();

  const eventBus = new EventBus();
  const mailer = MailerFactory.create(env);
  registerMailListeners(eventBus, mailer);

  return {
    eventBus,
    mailer,
    userRepository: new PrismaUserRepository(prisma),
    database: new PrismaDatabaseHealth(prisma),
  };
}
