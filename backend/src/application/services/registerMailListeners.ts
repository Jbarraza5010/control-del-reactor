import type { EventBus } from '../../shared/events/EventBus';
import type { Mailer } from '../ports/Mailer';

/**
 * Observador de los eventos de cuenta: cuando alguien se registra o pide recuperar su
 * contraseña, se envía el correo correspondiente. (Los enlaces reales los define Moisés.)
 */
export function registerMailListeners(bus: EventBus, mailer: Mailer): void {
  bus.subscribe('UserRegistered', async ({ email, verificationToken }) => {
    await mailer.send({
      to: email,
      subject: 'Verifica tu correo - Control del Reactor',
      text: `Tu código de verificación (válido 24 horas): ${verificationToken}`,
    });
  });

  bus.subscribe('PasswordResetRequested', async ({ email, resetToken }) => {
    await mailer.send({
      to: email,
      subject: 'Recupera tu contraseña - Control del Reactor',
      text: `Tu código para restablecer la contraseña (válido 1 hora): ${resetToken}`,
    });
  });
}
