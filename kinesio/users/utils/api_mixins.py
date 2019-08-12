from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


class LoggedUserPatchAPIViewMixin(APIView):
    """ Add a 'patch' method to views in order to do partial updated of the logged users,
        without requesting the user's PK."""
    def patch(self, request):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'wrong parameters'})


class LoggedUserDetailAPIViewMixin(APIView):
    """ Add a 'get' method to views in order to do return user data,
        without requesting the user's PK."""
    def get(self, request):
        return Response(self.serializer_class(request.user).data, status=status.HTTP_200_OK)
