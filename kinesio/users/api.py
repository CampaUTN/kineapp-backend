from rest_framework import generics
from rest_framework.views import APIView
from .models import CustomUser, SecretQuestion
from .serializers import CustomUserSerializer, SecretQuestionSerializer


class PatientsAPIView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.patients()
    serializer_class = CustomUserSerializer


class PatientDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.patients()
    serializer_class = CustomUserSerializer


class MedicsAPIView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.medics()
    serializer_class = CustomUserSerializer


class SecretQuestionAPIView(generics.ListCreateAPIView):
    queryset = SecretQuestion.objects.all()
    serializer_class = SecretQuestionSerializer


class CheckAnswerAPIView(APIView):

    def post(self, request):
        user_id = request.data.get('user_id', None)
        answer = request.data.get('answer', None)
        if Errors.is_invalid(user_id):
            return Errors.missing_field_error('user_id')
        elif Errors.is_invalid(answer):
            return Errors.missing_field_error('answer')
        else:
            #storedSecretAnswer = .objects.filter(user_id=user_id).order_by('-id')[:1]).data
            #print(storedSecretAnswer.id)

            return Response({'Status': 'a'}, status=HTTP_200_OK)