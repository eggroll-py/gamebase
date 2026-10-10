from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model

from .serializers import UserProfileSerializer, UserPublicSerializer

User = get_user_model()

class UserProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class UserProfileStatsView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data['stats'])

class UserPublicView(GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = UserPublicSerializer

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound(f"User '{username}' could not be found")
        serializer = self.get_serializer(user)
        return Response(serializer.data)


