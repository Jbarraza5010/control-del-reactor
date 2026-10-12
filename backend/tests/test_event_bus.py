from app.application.ports.mailer import MailMessage, Mailer
from app.application.services.register_mail_listeners import register_mail_listeners
from app.shared.events import EventBus, UserRegistered

EVENT = UserRegistered(user_id="u1", email="a@b.com", verification_token="tok")


class SpyMailer(Mailer):
    def __init__(self) -> None:
        self.sent: list[MailMessage] = []

    def send(self, message: MailMessage) -> None:
        self.sent.append(message)


def test_entrega_el_evento_a_todos_los_suscriptores():
    bus, a, b = EventBus(), [], []
    bus.subscribe(UserRegistered, a.append)
    bus.subscribe(UserRegistered, b.append)
    bus.publish(EVENT)
    assert a == [EVENT] and b == [EVENT]


def test_un_listener_que_falla_no_impide_que_los_demas_se_ejecuten():
    bus, ok = EventBus(), []

    def malo(_):
        raise RuntimeError("falla")

    bus.subscribe(UserRegistered, malo)
    bus.subscribe(UserRegistered, ok.append)
    bus.publish(EVENT)  # no debe lanzar
    assert ok == [EVENT]


def test_permite_cancelar_la_suscripcion():
    bus, got = EventBus(), []
    cancelar = bus.subscribe(UserRegistered, got.append)
    cancelar()
    bus.publish(EVENT)
    assert got == []


def test_user_registered_dispara_el_correo_de_verificacion():
    bus, mailer = EventBus(), SpyMailer()
    register_mail_listeners(bus, mailer)
    bus.publish(EVENT)
    assert len(mailer.sent) == 1
    assert mailer.sent[0].to == "a@b.com"
    assert "tok" in mailer.sent[0].text
