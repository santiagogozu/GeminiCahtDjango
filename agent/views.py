from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .langchain_agent import process_query

from twilio.twiml.messaging_response import MessagingResponse
import os
import logging
import requests  # ✅ Faltaba esta importación

from django.http import HttpResponse

logger = logging.getLogger(__name__)


class LangchainAgentView(APIView):
    def post(self, request, *args, **kwargs):
        print("Mensaje recibido:", request.data)
        query = request.data.get("query", "")
        try:
            result = process_query(query)
            return Response({"response": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WhatsAppWebhookView(APIView):
    def post(self, request):
        from_number = request.data.get("From", "")
        body = request.data.get("Body", "").strip()

        logger.info(f"Mensaje de WhatsApp recibido: {from_number} - {body}")
        print(f"Mensaje de WhatsApp recibido: {from_number} - {body}")

        query_data = {"query": body}
        query_url = (
            "http://localhost:8000/query/"  # Asegúrate de que tenga la barra final
        )

        try:
            response = requests.post(query_url, json=query_data)
            print(f"Respuesta cruda de /query/: {response.text}")

            try:
                response_data = response.json()
                if response.status_code == 200:
                    result = response_data.get(
                        "response", "No se pudo obtener respuesta."
                    )
                else:
                    result = "Error al procesar la consulta."
            except Exception as parse_error:
                result = f"Error al interpretar respuesta JSON: {parse_error}"

        except Exception as e:
            result = f"Error al contactar el servidor de consultas: {str(e)}"

        # Crear y devolver la respuesta XML que Twilio espera
        twiml_response = MessagingResponse()
        twiml_response.message(result)

        print("Respuesta que se enviará a Twilio:", str(twiml_response))

        return HttpResponse(str(twiml_response), content_type="application/xml")


# class WhatsAppWebhookView(APIView):
#   def post(self, request):
#       from_number = request.data.get('From', '')
#      body = request.data.get('Body', '').strip()
#
#       logger.info(f"Mensaje de WhatsApp recibido: {from_number} - {body}")
#
#       respuesta = f"Hola 👋, recibimos tu mensaje: '{body}'"
#
#       twiml_response = MessagingResponse()
#      twiml_response.message(respuesta)

#     return HttpResponse(str(twiml_response), content_type='application/xml')
#
