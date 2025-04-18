from django.urls import path
from .views import LangchainAgentView, WhatsAppWebhookView

urlpatterns = [
    path("query/", LangchainAgentView.as_view(), name="langchain_query"),
    path('whatsapp/webhook/', WhatsAppWebhookView.as_view(), name='whatsapp-webhook'),
]
