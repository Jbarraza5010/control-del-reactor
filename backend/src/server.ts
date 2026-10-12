import { loadEnv } from './config/env';
import { logger } from './shared/logger';
import { createApp } from './presentation/http/app';

const env = loadEnv();
const app = createApp();

const server = app.listen(env.PORT, () => {
  logger.info('Backend escuchando', { port: env.PORT, env: env.NODE_ENV });
});

function shutdown(signal: string): void {
  logger.info('Apagando servidor', { signal });
  server.close(() => process.exit(0));
}
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
