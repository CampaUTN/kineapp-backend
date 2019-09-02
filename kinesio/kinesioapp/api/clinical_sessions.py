from rest_framework import generics, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import ClinicalSession
from ..serializers import ClinicalSessionSerializer
from ..utils.api_mixins import GenericPatchViewWithoutPut


class ClinicalSessionAPIView(generics.CreateAPIView):
    serializer_class = ClinicalSessionSerializer


class ClinicalSessionsForPatientView(generics.ListAPIView):
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
    def get(self, request, patient_id):
        queryset = self.get_queryset().filter(patient_id=patient_id).accessible_by(request.user)
        serializer = self.serializer_class(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ClinicalSessionUpdateAPIView(GenericPatchViewWithoutPut):
    serializer_class = ClinicalSessionSerializer
    queryset = ClinicalSession.objects.all()

    @swagger_auto_schema(
        operation_id='patch_clinical_session',
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Updated clinical session",
                schema=ClinicalSessionSerializer(),
            )
        }
    )
    def patch(self, request, pk):
        return super().patch(request, pk)
