from rest_framework import generics, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView

from ..models import Exercise
from ..serializers import ExerciseSerializer
from ..utils.api_mixins import GenericPatchViewWithoutPut


class ExerciseCreateAPIView(generics.CreateAPIView):
    serializer_class = ExerciseSerializer

    @swagger_auto_schema(
        operation_id='exercise_create',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'video_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the video of the exercise.'),
                'days': openapi.Schema(type=openapi.TYPE_INTEGER, enum=[0, 1, 2, 3, 4, 5, 6])
            },
            required=['name', 'days']
        ),
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Missing or invalid parameter',
            ),
            status.HTTP_201_CREATED: openapi.Response(
                description="Exercise created successfully.",
                schema=ExerciseSerializer(many=True)
            )
        }
    )
    def post(self, request):
        if 'done' in request.POST:
            request.POST.pop('done')
        return super().post(request)

    def get_serializer(self, data):
        exercises = []
        days = data.pop('days')
        for day in days:
            exercise = data.copy()
            exercise['day'] = day
            exercises.append(exercise)
        return self.serializer_class(data=exercises, many=True)


class ExerciseUpdateAPIView(GenericPatchViewWithoutPut):
    serializer_class = ExerciseSerializer
    queryset = Exercise.objects.all()

    @swagger_auto_schema(
        operation_id='patch_exercise',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'video_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the video of the exercise.'),
                'done': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Set it to True after the patient finishes the exercise.')
            },
            required=['name', 'days']
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Updated exercise",
                schema=ExerciseSerializer(),
            )
        }
    )
    def patch(self, request, pk):
        return super().patch(request, pk)
