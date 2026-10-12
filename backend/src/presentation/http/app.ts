import express, { type Express } from 'express';
import { errorHandler } from './middlewares/errorHandler';
import { notFound } from './middlewares/notFound';
import { buildRouter, type RouterDeps } from './routes';

export function createApp(deps: RouterDeps): Express {
  const app = express();
  app.disable('x-powered-by');
  app.use(express.json({ limit: '100kb' }));
  app.use(buildRouter(deps));
  app.use(notFound);
  app.use(errorHandler);
  return app;
}
