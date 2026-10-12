export interface MailMessage {
  to: string;
  subject: string;
  text: string;
}

/** Puerto de salida: la aplicación pide "enviar un correo" sin saber cómo se envía. */
export interface Mailer {
  send(message: MailMessage): Promise<void>;
}
