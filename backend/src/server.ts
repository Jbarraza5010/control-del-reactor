import { loadEnv } from './config/env';
import { buildContainer } from './container';
import { disconnectPrisma } from './infrastructure/persistence/prisma/PrismaClientProvider';
import { createApp } from './presentation/http/app';
import { logger } from './shared/logger';

const env = loadEnv();
const container = buildContainer(env);
const app = createApp({ database: container.database });

const server = app.listen(env.PORT, () => {
  logger.info('Backend escuchando', { port: env.PORT, env: env.NODE_ENV });
});

function shutdown(signal: string): void {
  logger.info('Apagando servidor', { signal });
  server.close(async () => {
    await disconnectPrisma();
    process.exit(0);
  });
}
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
