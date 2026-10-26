import nodemailer, { type Transporter } from 'nodemailer';
import type { Mailer, MailMessage } from '../../application/ports/Mailer';

/** Producción: envío real por SMTP. */
export class SmtpMailer implements Mailer {
  private readonly transporter: Transporter;

  constructor(
    options: { host: string; port: number; user?: string; pass?: string },
    private readonly from: string,
  ) {
    this.transporter = nodemailer.createTransport({
      host: options.host,
      port: options.port,
      secure: options.port === 465,
      auth: options.user ? { user: options.user, pass: options.pass } : undefined,
    });
  }

  async send(message: MailMessage): Promise<void> {
    await this.transporter.sendMail({ from: this.from, ...message });
  }
}
