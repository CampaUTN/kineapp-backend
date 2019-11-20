from rest_framework import generics, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework.request import HttpRequest

from ..models import Exercise
from ..serializers import ExerciseSerializer
from ..utils.api_mixins import GenericPatchViewWithoutPut, GenericListView, GenericDeleteView


class ExercisesForPatientView(GenericListView):
    serializer_class = ExerciseSerializer
    queryset = Exercise.objects.all()

    @swagger_auto_schema(
        operation_id='exercises_for_patient',
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
                description="Exercises for the patient with the given ID. If there is no matching session, the list will be empty.",
                schema=ExerciseSerializer(many=True),
            )
        }
    )
    def get(self, request: HttpRequest, patient_id: int) -> Response:
        return super().get(request, queryset=self.queryset.filter(patient_id=patient_id))


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
                'days': openapi.Schema(type=openapi.TYPE_INTEGER, enum=[0, 1, 2, 3, 4, 5, 6]),
                'patient_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the patient to whom the exercise is assigned to.'),
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
    def post(self, request: HttpRequest) -> Response:
        if 'done' in request.POST:
            request.POST.pop('done')
        return super().post(request)

    def get_serializer(self, data: dict) -> ExerciseSerializer:
        exercises = []
        days = data.pop('days')
        for day in days:
            exercise = data.copy()
            exercise['day'] = day
            exercises.append(exercise)
        return self.serializer_class(data=exercises, many=True)


class ExerciseUpdateAndDeleteAPIView(GenericDeleteView, GenericPatchViewWithoutPut):
    serializer_class = ExerciseSerializer
    model_class = Exercise

    @swagger_auto_schema(
        operation_id='patch_exercise',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'day': openapi.Schema(type=openapi.TYPE_INTEGER, enum=[0, 1, 2, 3, 4, 5, 6]),
                'video_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the video of the exercise.'),
                'done': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Set it to True after the patient finishes the exercise.')
            },
        ),
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Invalid parameter',
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Exercise not related to the logged in user."
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Invalid exercise id: Exercise not found"
            ),
            status.HTTP_200_OK: openapi.Response(
                description="Updated exercise",
                schema=ExerciseSerializer(),
            )
        }
    )
    def patch(self, request: HttpRequest, id: int) -> Response:
        # This method exist only to add an '@swagger_auto_schema' annotation
        return super().patch(request, id)

    @swagger_auto_schema(
        operation_id='exercise_delete',
        manual_parameters=[
            openapi.Parameter(
                name='id', in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="Exercise's ID.",
                required=True
            ),
        ],
        responses={
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="User not authorized to delete that exercise."
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Invalid exercise id: Exercise not found"
            ),
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="Image deleted successfully.",
            ),
        }
    )
    def delete(self, request: HttpRequest, id: int) -> Response:
        # This method exist only to add an '@swagger_auto_schema' annotation
        return super().delete(request, id)
