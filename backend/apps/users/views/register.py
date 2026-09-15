from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import RegisterResponseSerializer, RegisterSerializer, UserSerializer
from apps.users.services import register_user


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=RegisterSerializer, responses={201: RegisterResponseSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = register_user(serializer.validated_data)
        return Response(
            {
                "user": UserSerializer(result["user"]).data,
                "refresh": result["refresh"],
                "access": result["access"],
            },
            status=status.HTTP_201_CREATED,
        )
