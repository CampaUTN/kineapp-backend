from rest_framework import generics, status
from .models import ClinicalHistory, ClinicalSession, Image
from .serializers import ClinicalHistorySerializer, ClinicalSessionSerializer, ImageSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ClinicalHistoryAPIView(generics.ListCreateAPIView):
    queryset = ClinicalHistory.objects.all()
    serializer_class = ClinicalHistorySerializer

@swagger_auto_schema(
    method='get',
    operation_id='get_clinical_histories',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING,
                                           description="token that generates when the user is logged"),
        },
        required=['token']
    ),
    responses={
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description="Missing or invalid token."
        ),
        status.HTTP_200_OK: openapi.Response(
            description="Clinical Histories",
            schema=ClinicalHistorySerializer(many=True)
        )
    }
)
@api_view(["GET"])
def get_clinical_histories(request):
    token = request.GET.get('token', None)
    if token is None:
        return Response({'message': 'Missing token'}, status=status.HTTP_400_BAD_REQUEST)
    else:

        try:
            user = Token.objects.get(key=token).user
            clinical_histories = ClinicalHistory.objects.filter(patient=user)
            clinical_serializer = ClinicalHistorySerializer(clinical_histories, many=True)
            return Response({'clinical_histories': clinical_serializer.data}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'message': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)
        except ClinicalHistory.DoesNotExist:
            return Response({'message': 'This user does not have clinical histories'}, status=status.HTTP_400_BAD_REQUEST)


class ClinicalSessionAPIView(generics.ListCreateAPIView):
    queryset = ClinicalSession.objects.all()
    serializer_class = ClinicalSessionSerializer


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def upload_image(request):
    description = request.data.get('description', '')
    try:
        content = request.data['content']
        date = request.data['date']
        clinical_session_id = request.data['clinical_session_id']
    except KeyError:
        return Response({'message': 'Missing parameter'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        Image.objects.create(content=content, description=description, date=date, clinical_session_id = clinical_session_id)
    except Exception as e:  
        return Response({'message': 'Error: ' + str(e) }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': 'Image created successfully'}, status=status.HTTP_201_CREATED)


class ImageDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
