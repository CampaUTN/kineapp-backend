from rest_framework import generics, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework.request import HttpRequest

from ..models import ClinicalSession
from ..serializers import ClinicalSessionSerializer
from ..utils.api_mixins import GenericPatchViewWithoutPut, GenericListView, GenericDeleteView


class ClinicalSessionAPIView(generics.CreateAPIView):
    serializer_class = ClinicalSessionSerializer


class ClinicalSessionsForPatientView(GenericListView):
    serializer_class = ClinicalSessionSerializer
    queryset = ClinicalSession.objects.all()

    @swagger_auto_schema(
        operation_id='clinical_sessions_for_patient',
        manual_parameters=[
            openapi.Parameter(
                name='patient_id', in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="Patient's ID.",
                required=True
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Clinical sessions for the patient with the given ID. If there is no matching session, the list will be empty.",
                schema=ClinicalSessionSerializer(many=True),
            )
        }
    )
    def get(self, request: HttpRequest, patient_id: int) -> Response:
        return super().get(request, queryset=self.queryset.filter(patient_id=patient_id))


class ClinicalSessionUpdateAndDeleteAPIView(GenericPatchViewWithoutPut, GenericDeleteView):
    serializer_class = ClinicalSessionSerializer
    model_class = ClinicalSession

    @swagger_auto_schema(
        operation_id='patch_clinical_session',
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Invalid parameter',
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Clinical session not related to the logged in user."
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Invalid clinical session id: Clinical session not found"
            ),
            status.HTTP_200_OK: openapi.Response(
                description="Updated clinical session",
                schema=ClinicalSessionSerializer(),
            )
        }
    )
    def patch(self, request: HttpRequest, id: int) -> Response:
        # This method exist only to add an '@swagger_auto_schema' annotation
        return super().patch(request, id)

    @swagger_auto_schema(
        operation_id='clinical_session_delete',
        operation_description='You will not be able to delete the session if the logged user does not have access.',
        manual_parameters=[
            openapi.Parameter(
                name='id', in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="Clinical Session's ID.",
                required=True
            ),
        ],
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Invalid parameter',
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="User not authorized to access that image. Only the patient and its medic can access the session."
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Invalid image id: Clinical Session not found"
            ),
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="Clinical Session deleted successfully."
            ),
        }
    )
    def delete(self, request: HttpRequest, id: int) -> Response:
        # This method exist only to add an '@swagger_auto_schema' annotation
        return super().delete(request, id)
