from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .langchain_agent import process_query

from twilio.twiml.messaging_response import MessagingResponse
import os
import logging
import requests

from django.http import HttpResponse


from django.conf import settings
import logging

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


# class WhatsAppWebhookView(APIView):
#     def post(self, request):
#         from_number = request.data.get("From", "")
#         body = request.data.get("Body", "").strip()

#         logger.info(f"Mensaje de WhatsApp recibido: {from_number} - {body}")
#         print(f"Mensaje de WhatsApp recibido: {from_number} - {body}")

#         query_data = {"query": body}
#         query_url = (
#             "http://localhost:8000/query/"  # Asegúrate de que tenga la barra final
#         )

#         try:
#             response = requests.post(query_url, json=query_data)
#             print(f"Respuesta cruda de /query/: {response.text}")

#             try:
#                 response_data = response.json()
#                 if response.status_code == 200:
#                     result = response_data.get(
#                         "response", "No se pudo obtener respuesta."
#                     )
#                 else:
#                     result = "Error al procesar la consulta."
#             except Exception as parse_error:
#                 result = f"Error al interpretar respuesta JSON: {parse_error}"

#         except Exception as e:
#             result = f"Error al contactar el servidor de consultas: {str(e)}"

#         # Crear y devolver la respuesta XML que Twilio espera
#         twiml_response = MessagingResponse()
#         twiml_response.message(result)

#         print("Respuesta que se enviará a Twilio:", str(twiml_response))

#         return HttpResponse(str(twiml_response), content_type="application/xml")


class WhatsAppWebhookView(APIView):
    def post(self, request):
        from_number = request.data.get("From", "")
        body = request.data.get("Body", "").strip()
        num_media = int(request.data.get("NumMedia", 0))

        logger.info(f"Mensaje de WhatsApp recibido: {from_number} - {body}")
        print(f"Mensaje de WhatsApp recibido: {from_number} - {body}")

        twiml_response = MessagingResponse()

        if num_media > 0:
            media_url = request.data.get("MediaUrl0")
            content_type = request.data.get("MediaContentType0")

            # Ruta donde guardar la imagen
            media_dir = os.path.join(settings.BASE_DIR, "img")
            os.makedirs(media_dir, exist_ok=True)

            # Nombre del archivo
            ext = content_type.split("/")[-1]
            file_name = f"{from_number.replace(':', '_')}_media.{ext}"
            file_path = os.path.join(media_dir, file_name)
        try:
            # 1) Imprime la URL y el tipo de medio que estás descargando
            logger.info(
                f"Descargando media desde: {media_url} (Content-Type: {content_type})"
            )

            # 2) Haz la petición con autenticación
            img_resp = requests.get(
                media_url,
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                timeout=10,
            )

            # 3) Log del status y headers
            logger.info(f"Twilio respondió con status {img_resp.status_code}")
            logger.debug(f"Headers de respuesta: {img_resp.headers}")

            # 4) Si no es 200, vuelca el body como texto para ver el XML o error
            if img_resp.status_code != 200:
                logger.error(f"Error al descargar media: {img_resp.text}")
                raise Exception(f"Descarga fallida con status {img_resp.status_code}")

            # 5) Guarda el contenido
            img_data = img_resp.content
            with open(file_path, "wb") as f:
                f.write(img_data)

            logger.info(f"Imagen guardada en {file_path}")
            twiml_response.message("Procesando imagen. Gracias por enviarla 📷")

        except Exception as e:
            # 6) Ahora el log incluirá exactamente qué pasó
            logger.exception("Error al guardar imagen")
            twiml_response.message(
                "Error al guardar la imagen. Revisa los logs para más detalles."
            )
        else:
            # Lógica para texto
            query_data = {"query": body}
            query_url = "http://localhost:8000/query/"

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

            twiml_response.message(result)

        print("Respuesta que se enviará a Twilio:", str(twiml_response))
        return HttpResponse(str(twiml_response), content_type="application/xml")
