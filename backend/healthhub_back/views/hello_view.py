from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class HelloList(APIView):
    def get(self, request):
        return Response(data={"message": "Hello, world!"}, status=status.HTTP_200_OK)