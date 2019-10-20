from rest_framework import generics
from rest_framework.permissions import AllowAny

from ..models import SecretQuestion
from ..serializers import SecretQuestionSerializer


class SecretQuestionAPIView(generics.ListAPIView):
    queryset = SecretQuestion.objects.all()
    serializer_class = SecretQuestionSerializer
    permission_classes = (AllowAny,)
