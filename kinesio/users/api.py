from rest_framework.response import Response
from rest_framework import generics, status
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


class SecretQuestionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SecretQuestion.objects.all()
    serializer_class = SecretQuestionSerializer


class CheckAnswerAPIView(APIView):

    def post(self, request):
        try:
            user_id = request.data['user_id']
            secret_question_id = request.data['secret_question_id']
            answer = request.data['answer']
        except KeyError:
            return Response({'message': 'Missing parameter'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(id=user_id, secret_question_id=secret_question_id)
        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

        compare = user.check_password(answer)

        return Response({'compare': compare}, status=status.HTTP_200_OK)

        
