import requests
import pytz
import datetime

from django.core.mail import send_mail
from celery.utils.log import get_task_logger
from celery import shared_task
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from notification_service.settings import config, EMAIL_HOST_USER
from .models import Message, Client, Mailing
from notification_service.celery import app

logger = get_task_logger(__name__)

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


@shared_task
def get_mailing_stat():
    mailing = Mailing.objects.all()
    total_count = mailing.count()
    result = []
    for mail in mailing:
        msg = Message.objects.filter(mailing=mail).all()
        group_sent = msg.filter(sending_status='sent').count()
        group_no_sent = msg.filter(sending_status='no sent').count()
        res = f'Mailing {mail.id} - {mail.time_start} - {mail.time_end};' \
              f' Total messages: {len(msg)}; Sent: {group_sent}; No sent: {group_no_sent};'
        result.append(res)
    context = {
        'mailings': total_count,
        'msg': result
    }
    html_template = render_to_string(template_name='mailings/mailings_stat.html',
                                     context=context)
    html_template = strip_tags(html_template)
    subject = f'Статистика рассылок за {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}'

    send_mail(subject, html_template, EMAIL_HOST_USER, ['test@2.ru'], fail_silently=True)
