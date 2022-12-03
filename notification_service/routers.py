from rest_framework import routers

from mailings.views import ClientViewSet, MessageViewSet, MailingViewSet

router = routers.DefaultRouter()
router.register('clients', ClientViewSet, basename='Управление клиентами')
router.register('messages', MessageViewSet)
router.register('mailings', MailingViewSet)
