import { describe, expect, it, vi } from 'vitest';
import type { Mailer } from '../src/application/ports/Mailer';
import { registerMailListeners } from '../src/application/services/registerMailListeners';
import { EventBus } from '../src/shared/events/EventBus';

const payload = { userId: 'u1', email: 'a@b.com', verificationToken: 'tok' };

describe('EventBus (Observer)', () => {
  it('entrega el evento a todos los suscriptores', async () => {
    const bus = new EventBus();
    const a = vi.fn();
    const b = vi.fn();
    bus.subscribe('UserRegistered', a);
    bus.subscribe('UserRegistered', b);
    await bus.publish('UserRegistered', payload);
    expect(a).toHaveBeenCalledWith(payload);
    expect(b).toHaveBeenCalledWith(payload);
  });

  it('un listener que falla no impide que los demás se ejecuten', async () => {
    const bus = new EventBus();
    const ok = vi.fn();
    bus.subscribe('UserRegistered', () => { throw new Error('falla'); });
    bus.subscribe('UserRegistered', ok);
    await expect(bus.publish('UserRegistered', payload)).resolves.toBeUndefined();
    expect(ok).toHaveBeenCalled();
  });

  it('permite cancelar la suscripción', async () => {
    const bus = new EventBus();
    const l = vi.fn();
    const off = bus.subscribe('UserRegistered', l);
    off();
    await bus.publish('UserRegistered', payload);
    expect(l).not.toHaveBeenCalled();
  });

  it('UserRegistered dispara el envío del correo de verificación', async () => {
    const bus = new EventBus();
    const send = vi.fn().mockResolvedValue(undefined);
    const mailer: Mailer = { send };
    registerMailListeners(bus, mailer);
    await bus.publish('UserRegistered', payload);
    expect(send).toHaveBeenCalledWith(expect.objectContaining({ to: 'a@b.com' }));
  });
});
