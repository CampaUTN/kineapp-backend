from rest_framework.response import Response
from rest_framework import status, generics
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.request import HttpRequest

from ..models import User
from ..serializers import PatientUserSerializer, MedicUserSerializer
from kinesioapp.utils.api_mixins import GenericPatchViewWithoutPut, GenericDetailsView, GenericListView


class CurrentPatientDetailUpdateAPIView(GenericPatchViewWithoutPut, GenericDetailsView):
    model_class = User
    serializer_class = PatientUserSerializer

    @swagger_auto_schema(
        operation_id='get_current_patient',
        responses={
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Users are not authorized to patch other users"
            ),
            status.HTTP_200_OK: openapi.Response(
                description="Current patient data",
                schema=PatientUserSerializer(),
            )
        }
    )
    def get(self, request: HttpRequest) -> Response:
        # This method exist only to add an '@swagger_auto_schema' annotation
        return super().get(request, request.user.id)

    @swagger_auto_schema(
        operation_id='patch_current_patient',
        operation_description='Patch the current patient. You can use 0 or negative integers to unset the current medic. Do not use \'null\' for that purpose!.',
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Invalid parameter',
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Users are not authorized to patch other users"
            ),
            status.HTTP_200_OK: openapi.Response(
                description="Current patient data",
                schema=PatientUserSerializer(),
            )
        }
    )
    def patch(self, request: HttpRequest) -> Response:
        return super().patch(request, request.user.id)


class MedicListAPIView(generics.ListAPIView):
    queryset = User.objects.medics()
    serializer_class = MedicUserSerializer
