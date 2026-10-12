/** Contrato genérico de repositorio (patrón Repository). */
export interface Repository<T, ID = string> {
  findById(id: ID): Promise<T | null>;
  save(entity: T): Promise<T>;
}
