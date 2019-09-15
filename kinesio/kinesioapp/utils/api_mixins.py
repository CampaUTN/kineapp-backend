from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404


class GenericPatchViewWithoutPut(APIView):
    def patch(self, request, id: int) -> Response:
        instance = get_object_or_404(self.model_class, id=id)
        if not instance.can_edit_and_delete(request.user):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'message': 'The user has no rights to modify or delete the current object.'})
        else:
            serializer = self.serializer_class(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK, data=serializer.data)
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'message': 'The id is valid but other parameters are invalid.'})


class GenericDeleteView(APIView):
    def delete(self, request, id: int) -> Response:
        instance = get_object_or_404(self.model_class, id=id)
        if not instance.can_edit_and_delete(request.user):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'message': 'The user has no rights to modify or delete the current object.'})
        else:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


# fixme: remove if unused
class GenericListView(APIView):
    def get(self, request) -> Response:
        queryset = self.get_queryset().accessible_by(request.user)
        serializer = self.serializer_class(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class GenericDetailsView(APIView):
    def get(self, request, id) -> Response:
        instance = get_object_or_404(self.model_class, id=id)
        if not instance.can_view(request.user):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'message': 'The user has no rights to view the current object.'})
        serializer = self.serializer_class(instance)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
