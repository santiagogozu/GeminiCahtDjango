# import pytest
# from unittest.mock import patch
# import requests
# from agent.langchain_agent import get_todays_date, get_physicochemical_report


# def test_get_todays_date_format():
#     result = get_todays_date()
#     assert "Hoy es" in result


# @patch("agent.langchain_agent.requests.get")
# def test_get_physicochemical_report_valid(mock_get):
#     mock_get.return_value.status_code = 200
#     mock_get.return_value.raise_for_status = lambda: None

#     result = get_physicochemical_report("abc123")
#     print("get_physicochemical_report :-----", result)
#     assert "url" in result
#     assert "report_id" in result


# def test_get_physicochemical_report_empty():
#     result = get_physicochemical_report("")
#     print("Resultado para entrada vacía:-----", result)
#     assert "Entrada vacía" in result


# @patch("agent.langchain_agent.requests.get")
# def test_get_physicochemical_report_http_error(mock_get):
#     mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError(
#         "404 Not Found"
#     )

#     with pytest.raises(ValueError) as exc_info:
#         get_physicochemical_report("xyz456")


# #     assert "No se pudo encontrar el reporte fisicoquímico" in str(exc_info.value)


# import pytest
# from django.urls import reverse
# from rest_framework import status
# from unittest.mock import patch, MagicMock
# from rest_framework.test import APIClient
# from twilio.twiml.messaging_response import MessagingResponse


# # Usar pytest-django para configurar el entorno de pruebas
# @pytest.fixture
# def client():
#     return APIClient()


# # Pruebas para LangchainAgentView
# @pytest.mark.django_db
# def test_langchain_agent_view_success(client):
#     # Simulando la respuesta de process_query
#     with patch("myapp.views.process_query", return_value="Respuesta de prueba"):
#         response = client.post(reverse("langchain_query"), {"query": "Test query"})

#     assert response.status_code == status.HTTP_200_OK
#     assert response.data["response"] == "Respuesta de prueba"


# @pytest.mark.django_db
# def test_langchain_agent_view_error(client):
#     # Simulando un error en process_query
#     with patch("myapp.views.process_query", side_effect=Exception("Error interno")):
#         response = client.post(reverse("langchain_query"), {"query": "Test query"})

#     assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
#     assert response.data["error"] == "Error interno"


# # Pruebas para WhatsAppWebhookView
# @pytest.mark.django_db
# @patch(
#     "myapp.views.requests.post"
# )  # Parcheamos requests.post para simular la comunicación externa
# def test_whatsapp_webhook_view_success(mock_post, client):
#     # Simulamos la respuesta de la API de /query/
#     mock_response = MagicMock()
#     mock_response.status_code = 200
#     mock_response.json.return_value = {"response": "Respuesta de prueba"}
#     mock_post.return_value = mock_response

#     data = {
#         "From": "+1234567890",
#         "Body": "Mensaje de prueba",
#     }

#     response = client.post(reverse("whatsapp-webhook"), data)

#     # Verificamos la respuesta a Twilio
#     assert response.status_code == 200
#     assert "Content-Type" in response._headers
#     assert response.content.decode().startswith(
#         '<?xml version="1.0" encoding="UTF-8"?>'
#     )
#     assert "Respuesta de prueba" in response.content.decode()


# @pytest.mark.django_db
# @patch(
#     "myapp.views.requests.post"
# )  # Parcheamos requests.post para simular la comunicación externa
# def test_whatsapp_webhook_view_query_error(mock_post, client):
#     # Simulamos una falla en la comunicación con /query/
#     mock_response = MagicMock()
#     mock_response.status_code = 500
#     mock_response.json.return_value = {"error": "Error al procesar consulta"}
#     mock_post.return_value = mock_response

#     data = {
#         "From": "+1234567890",
#         "Body": "Mensaje de prueba",
#     }

#     response = client.post(reverse("whatsapp-webhook"), data)

#     # Verificamos la respuesta a Twilio en caso de error
#     assert response.status_code == 200
#     assert "Content-Type" in response._headers
#     assert response.content.decode().startswith(
#         '<?xml version="1.0" encoding="UTF-8"?>'
#     )
#     assert "Error al procesar la consulta." in response.content.decode()


# @pytest.mark.django_db
# @patch(
#     "myapp.views.requests.post"
# )  # Parcheamos requests.post para simular la comunicación externa
# def test_whatsapp_webhook_view_json_error(mock_post, client):
#     # Simulamos una respuesta incorrecta (no JSON válido)
#     mock_response = MagicMock()
#     mock_response.status_code = 200
#     mock_response.text = "Respuesta no JSON"
#     mock_post.return_value = mock_response

#     data = {
#         "From": "+1234567890",
#         "Body": "Mensaje de prueba",
#     }

#     response = client.post(reverse("whatsapp-webhook"), data)

#     # Verificamos que se maneje el error de interpretación del JSON
#     assert response.status_code == 200
#     assert "Content-Type" in response._headers
#     assert response.content.decode().startswith(
#         '<?xml version="1.0" encoding="UTF-8"?>'
#     )
#     assert "Error al interpretar respuesta JSON" in response.content.decode()

import pytest
from unittest.mock import patch, Mock
from rest_framework.test import APIClient
from django.urls import reverse
from agent.langchain_agent import get_todays_date, get_physicochemical_report


# def test_get_physicochemical_report_valid():

#     result = get_physicochemical_report("AMGQ01")
#     assert "url" in result
#     assert "report_id" in result


# def test_get_physicochemical_report_not_valid():
#     with pytest.raises(ValueError) as excinfo:
#         get_physicochemical_report("abc123")
#     assert "No se pudo encontrar el reporte fisicoquímico" in str(excinfo.value)


from unittest.mock import patch, MagicMock


@pytest.mark.django_db
def test_whatsapp_webhook_e2e_success():
    # Crea un cliente que simula peticiones HTTP al servidor Django, sin levantar el servidor real.
    client = APIClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "Hola desde LangChain 🤖"}
    mock_response.text = '{"response": "Hola desde LangChain 🤖"}'

    # Mockea requests.post en el archivo agent.views (donde se usa)
    with patch("agent.views.requests.post", return_value=mock_response):
        response = client.post(
            reverse("whatsapp-webhook"),
            data={
                "From": "whatsapp:+573001234567",
                "Body": "Hola desde twilio",
            },
            format="multipart",
        )
    assert response.status_code == 200
    assert "<Response>" in response.content.decode()
    assert "Hola desde LangChain" in response.content.decode()
