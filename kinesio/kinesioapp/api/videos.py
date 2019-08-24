from rest_framework import generics, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.views import APIView
# For the hardcoded image only:
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt

from ..models import Image, ClinicalSession, Video
from ..serializers import ClinicalSessionSerializer, ImageSerializer, VideoSerializer
from ..utils.download import download
from .. import choices
from ..utils.api_mixins import GenericPatchViewWithoutPut, GenericListView


class UploadVideoAPIView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        try:
            uploaded_file = request.data.get('file')
            name = request.data.get('name')
            medic_id = request.data.get('medic_id')
        except KeyError:
            return Response({'message': 'Missing or invalid file, name or medic_id.'}, status=status.HTTP_400_BAD_REQUEST)
        content = uploaded_file.read()
        video = Video.objects.create(name=name, content=content, medic_id=medic_id)
        return Response(VideoSerializer(video).data, status=status.HTTP_201_CREATED)


class DeleteVideoAPIView(generics.DestroyAPIView):
    model = Video
    queryset = Video.objects.all()  # is it necessary?
