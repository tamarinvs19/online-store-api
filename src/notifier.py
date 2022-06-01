from copy import deepcopy
import datetime as dt
import smtplib
import ssl

import config as cfg


def send_email(email: str) -> None:
    smtp_server = "smtp.gmail.com"
    port = 465

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(cfg.EMAIL, cfg.PASSWORD)
            server.sendmail(
                cfg.EMAIL,
                email,
                'We are glad to see you again in our service!',
            )
    except Exception as e:
        print(e)


class Notifier:
    obj = None

    delay = dt.timedelta(hours=1)
    tasks: dict[str, dt.datetime] = {}

    @classmethod
    def __new__(cls, *args):
        if cls.obj is None:
            cls.obj = object.__new__(cls)
        return cls.obj

    def update_task(self, email: str) -> None:
        self.tasks[email] = dt.datetime.now() + self.delay

    def schedule(self) -> None:
        now = dt.datetime.now()
        for email, time in deepcopy(self.tasks).items():
            if time <= now:
                send_email(email)
                self.tasks.pop(email)

