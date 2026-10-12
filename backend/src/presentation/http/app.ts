import express, { type Express } from 'express';
import { errorHandler } from './middlewares/errorHandler';
import { notFound } from './middlewares/notFound';
import { buildRouter } from './routes';

export function createApp(): Express {
  const app = express();
  app.disable('x-powered-by');
  app.use(express.json({ limit: '100kb' }));
  app.use(buildRouter());
  app.use(notFound);
  app.use(errorHandler);
  return app;
}
