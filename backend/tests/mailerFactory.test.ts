import { describe, expect, it } from 'vitest';
import { ConsoleMailer } from '../src/infrastructure/mail/ConsoleMailer';
import { MailerFactory } from '../src/infrastructure/mail/MailerFactory';
import { SmtpMailer } from '../src/infrastructure/mail/SmtpMailer';

const base = { SMTP_PORT: 587, MAIL_FROM: 'x@y.com' } as const;

describe('MailerFactory (Factory)', () => {
  it('console -> ConsoleMailer', () => {
    expect(MailerFactory.create({ ...base, MAIL_TRANSPORT: 'console' })).toBeInstanceOf(ConsoleMailer);
  });

  it('smtp con host -> SmtpMailer', () => {
    expect(MailerFactory.create({ ...base, MAIL_TRANSPORT: 'smtp', SMTP_HOST: 'smtp.test' })).toBeInstanceOf(SmtpMailer);
  });

  it('smtp sin host -> error de configuración', () => {
    expect(() => MailerFactory.create({ ...base, MAIL_TRANSPORT: 'smtp' })).toThrow(/SMTP_HOST/);
  });
});
