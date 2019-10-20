from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.request import HttpRequest

from ..models import User
from ..serializers import MedicUserSerializer, RelatedPatientsSerializer, RelatedPatientsDocumentationSerializer
from kinesioapp.utils.api_mixins import GenericPatchViewWithoutPut, GenericDetailsView, GenericListView


class PatientListAPIView(GenericListView):
    serializer_class = RelatedPatientsSerializer
    queryset = User.objects.patients()

    @swagger_auto_schema(
        operation_id='get_related_patients',
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Data from patients of the current medic. If used as a patient, it will fail.",
                schema=RelatedPatientsDocumentationSerializer(),
            )
        }
    )
    def get(self, request: HttpRequest) -> Response:
        serializer = self.serializer_class(request.user)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class CurrentMedicDetailUpdateAPIView(GenericPatchViewWithoutPut, GenericDetailsView):
    model_class = User
    serializer_class = MedicUserSerializer

    @swagger_auto_schema(
        operation_id='get_current_medic',
        responses={
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="You can not get this user's information as it is not related to you in any way."
            ),
            status.HTTP_200_OK: openapi.Response(
                description="Current medic's data",
                schema=MedicUserSerializer(),
            )
        }
    )
    def get(self, request: HttpRequest) -> Response:
        # This method exist only to add an '@swagger_auto_schema' annotation
        return super().get(request, request.user.id)

    @swagger_auto_schema(
        operation_id='patch_current_medic',
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Invalid parameter',
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Users are not authorized to patch other users"
            ),
            status.HTTP_200_OK: openapi.Response(
                description="Current patient data",
                schema=MedicUserSerializer(),
            )
        }
    )
    def patch(self, request: HttpRequest) -> Response:
        # This method exist only to add an '@swagger_auto_schema' annotation
        return super().patch(request, request.user.id)
