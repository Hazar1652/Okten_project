from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import HangoutObjectPermission
from apps.hangout.serializers import HangoutRequestSerializer
from apps.hangout.services import close_hangout, get_hangouts_queryset

class HangoutCloseView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, HangoutObjectPermission]
    serializer_class = HangoutRequestSerializer

    def get_queryset(self):
        return get_hangouts_queryset(self.request)

    def post(self, request, *args, **kwargs):
        hangout = close_hangout(self.get_object(), request.user)
        return Response(
            HangoutRequestSerializer(hangout, context={"request": request}).data
        )
