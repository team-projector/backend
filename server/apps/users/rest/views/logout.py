from rest_framework.response import Response
from rest_framework.views import APIView


class LogoutView(APIView):
    def post(self, request):
        request.auth.delete()

        return Response()
