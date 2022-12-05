from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets

from .models import Mailing, Client, Message
from .serializers import MailingSerializer, ClientSerializer, MessageSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """API клиента"""
    serializer_class = ClientSerializer
    queryset = Client.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Создание Клиента
        """
        return super().create(request)

    def list(self, request, *args, **kwargs):
        """
        Список клиентов
        """
        return super().list(request)

    def retrieve(self, request, *args, **kwargs):
        """
        Получить клиента по id
        """
        return super().retrieve(request)

    def update(self, request, *args, **kwargs):
        """
        Обновить клиента по id
        """
        return super().update(request)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()


class MailingViewSet(viewsets.ModelViewSet):
    serializer_class = MailingSerializer
    queryset = Mailing.objects.all()

    @action(detail=True, methods=['get'])
    def info(self, request, pk=None):
        """
        Summary data for a specific mailing list
        """
        queryset_mailing = Mailing.objects.all()
        get_object_or_404(queryset_mailing, pk=pk)
        queryset = Message.objects.filter(mailing_id=pk).all()
        serializer = MessageSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def full_info(self, request):
        """
        Summary data for all mailings
        """
        mailing = Mailing.objects.all()
        total_count = mailing.count()
        content = {'Total number of mailings': total_count,
                   'The number of messages sent': ''}
        result = {}

        for mail in mailing:
            res = {'Total messages': 0, 'Sent': 0, 'No sent': 0}
            msg = Message.objects.filter(mailing=mail).all()
            group_sent = msg.filter(sending_status='sent').count()
            group_no_sent = msg.filter(sending_status='no sent').count()
            res['Total messages'] = len(msg)
            res['Sent'] = group_sent
            res['No sent'] = group_no_sent
            row = f'mailing id: {mail.id} - start {mail.time_start} - end {mail.time_end}'
            result[row] = res

        content['The number of messages sent'] = result
        return Response(content)
