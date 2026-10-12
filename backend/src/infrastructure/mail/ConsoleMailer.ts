import type { Mailer, MailMessage } from '../../application/ports/Mailer';
import { logger } from '../../shared/logger';

/** Desarrollo: imprime el correo en el log (útil para copiar el enlace de verificación). */
export class ConsoleMailer implements Mailer {
  async send(message: MailMessage): Promise<void> {
    logger.info('[correo simulado]', { to: message.to, subject: message.subject, text: message.text });
  }
}
