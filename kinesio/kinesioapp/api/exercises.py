from rest_framework import generics, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView

from ..models import Exercise
from ..serializers import ExerciseSerializer
from ..utils.api_mixins import GenericPatchViewWithoutPut


class ExerciseCreateAPIView(generics.CreateAPIView):
    @swagger_auto_schema(
        operation_id='exercise_create',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'patient_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='Image content as base64 string. Be careful to not include extra quotes.'),
                'tag': openapi.Schema(type=openapi.TYPE_INTEGER, enum=[0, 1, 2, 3, 4, 5, 6]),
            },
            required=['clinical_session_id', 'content', 'tag']
        ),
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Missing or invalid clinical_session_id, tag or content',
            ),
            status.HTTP_201_CREATED: openapi.Response(
                description="Image created successfully.",
                schema=ThumbnailSerializer()
            )
        }
    )
    def post(self, request):
        return super().post(request)


class ExerciseUpdateAPIView(GenericPatchViewWithoutPut):
    serializer_class = ExerciseSerializer
    queryset = Exercise.objects.all()

    @swagger_auto_schema(
        operation_id='patch_exercise',
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Updated exercise",
                schema=ExerciseSerializer(),
            )
        }
    )
    def patch(self, request, pk):
        return super().patch(request, pk)
