from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


class GenericPatchViewWithoutPut(APIView):
    """ Add a 'patch' method to views in order to do partial updated of the logged users,
        without requesting the user's PK."""
    def patch(self, request, pk):
        instance = self.get_queryset().get(pk=pk)
        if not instance.can_access(request.user):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'message': 'The user has no rights to patch the current object.'})
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={'message': 'The id is valid but other parameters are invalid.'})

    def get_queryset(self):
        return self.queryset


# fixme remove if unused
class GenericListView(APIView):
    """ Add a 'get' method to views in order to only get instances that are accessible by the logged user. """
    def get(self, request):
        queryset = self.get_queryset().accessible_by(request.user)
        serializer = self.serializer_class(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
