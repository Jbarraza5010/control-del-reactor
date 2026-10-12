import { logger } from '../logger';

/**
 * Patrón Observer: un bus de eventos tipado dentro del proceso.
 * Quien publica (el servicio de cuentas) no conoce a quien escucha (el envío de correos),
 * así se agregan reacciones nuevas sin modificar el servicio.
 * En el Sprint 3 el mismo mecanismo propagará puntajes y ranking (ERS 7.3).
 */
export interface DomainEvents {
  UserRegistered: { userId: string; email: string; verificationToken: string };
  PasswordResetRequested: { userId: string; email: string; resetToken: string };
}

export type EventName = keyof DomainEvents;
type Listener<K extends EventName> = (payload: DomainEvents[K]) => void | Promise<void>;

export class EventBus {
  private readonly listeners: { [K in EventName]?: Listener<K>[] } = {};

  subscribe<K extends EventName>(event: K, listener: Listener<K>): () => void {
    const list = (this.listeners[event] ??= []) as Listener<K>[];
    list.push(listener);
    return () => {
      const i = list.indexOf(listener);
      if (i >= 0) list.splice(i, 1);
    };
  }

  /** Un listener que falla NO rompe a los demás ni a quien publicó: se registra el error. */
  async publish<K extends EventName>(event: K, payload: DomainEvents[K]): Promise<void> {
    const list = (this.listeners[event] ?? []) as Listener<K>[];
    await Promise.all(
      list.map(async (listener) => {
        try {
          await listener(payload);
        } catch (err) {
          logger.error('Falló un listener de evento', {
            event,
            message: err instanceof Error ? err.message : String(err),
          });
        }
      }),
    );
  }
}
