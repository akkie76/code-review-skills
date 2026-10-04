from model import Notice


class DeliveryError(Exception):
    pass


class Sender:
    def __init__(self, deliver) -> None:
        self.deliver = deliver

    def send(self, notice: Notice) -> None:
        self.deliver(notice.recipient, notice.subject, notice.body)
