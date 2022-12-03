import os
import requests
import pytz
import datetime
from celery.utils.log import get_task_logger
from django.conf import settings

from .models import Message, Client, Mailing
from notification_service.celery import app

logger = get_task_logger(__name__)

config = settings.config

URL = config.sender_api.url
TOKEN = config.sender_api.token


@app.task(bind=True, retry_backoff=True)
def send_message(self, data, client_id, mailing_id, url=URL, token=TOKEN):
    mail = Mailing.objects.get(pk=mailing_id)
    client = Client.objects.get(pk=client_id)
    timezone = pytz.timezone(client.timezone)
    now = datetime.datetime.now(timezone)

    if mail.time_start <= now.time() <= mail.time_end:
        header = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'}
        try:
            requests.post(url=url + str(data['id']), headers=header, json=data)
        except requests.exceptions.RequestException as exc:
            logger.error(
                f"Message: Сообщение {data} не отправлено. Ошибка на стороне api {url}. Ошибка - {exc}")
            raise self.retry(exc=exc)
        else:
            logger.info(f"Message id: {data['id']}, Sending status: 'Sent'")
            Message.objects.filter(pk=data['id']).update(sending_status='Sent')
    else:
        time = 24 - (int(now.time().strftime('%H:%M:%S')[:2]) -
                     int(mail.time_start.strftime('%H:%M:%S')[:2]))
        logger.info(f"Message id: {data['id']}, "
                    f"The current time is not for sending the message,"
                    f"restarting task after {60 * 60 * time} seconds")
        return self.retry(countdown=60 * 60 * time)
