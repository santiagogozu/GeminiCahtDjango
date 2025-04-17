from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .langchain_agent import process_query


class LangchainAgentView(APIView):
    def post(self, request):
        query = request.data.get("query", "")
        try:
            result = process_query(query)
            return Response({"response": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
