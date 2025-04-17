from django.urls import path
from .views import LangchainAgentView

urlpatterns = [
    path("query/", LangchainAgentView.as_view(), name="langchain_query"),
]
