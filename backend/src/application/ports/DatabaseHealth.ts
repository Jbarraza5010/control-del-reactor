/** Puerto: permite al health check preguntar "¿hay base de datos?" sin conocer Prisma. */
export interface DatabaseHealth {
  ping(): Promise<void>;
}
