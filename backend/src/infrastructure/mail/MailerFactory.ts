import type { Mailer } from '../../application/ports/Mailer';
import type { Env } from '../../config/env';
import { ConsoleMailer } from './ConsoleMailer';
import { SmtpMailer } from './SmtpMailer';

/**
 * Patrón Factory: decide QUÉ implementación de Mailer crear según la configuración.
 * El resto del sistema solo ve la interfaz Mailer.
 */
export class MailerFactory {
  static create(env: Pick<Env, 'MAIL_TRANSPORT' | 'SMTP_HOST' | 'SMTP_PORT' | 'SMTP_USER' | 'SMTP_PASS' | 'MAIL_FROM'>): Mailer {
    switch (env.MAIL_TRANSPORT) {
      case 'smtp':
        if (!env.SMTP_HOST) throw new Error('MAIL_TRANSPORT=smtp requiere SMTP_HOST');
        return new SmtpMailer(
          { host: env.SMTP_HOST, port: env.SMTP_PORT, user: env.SMTP_USER, pass: env.SMTP_PASS },
          env.MAIL_FROM,
        );
      case 'console':
      default:
        return new ConsoleMailer();
    }
  }
}
