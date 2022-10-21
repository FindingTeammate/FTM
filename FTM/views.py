from django.shortcuts import render
from rest_framework import generics, status
from .models import Profile, WorkExp, Reviews
from .serializer import ProfileSerializer, WorkExpSerializer, ReviewsSerializer, UserSerializer, RegisterSerializer
# from .serializer import CreateProfileSerializer, CreateReviewSerializer, CreateWorkExpSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets


# class UserDetailAPI(APIView):
#   authentication_classes = (TokenAuthentication,)
#   permission_classes = (AllowAny,)
#   def get(self,request,*args,**kwargs):
#     user = User.objects.get(id=request.user.id)
#     serializer = UserSerializer(user)
#     return Response(serializer.data)


class RegisterUserAPIView(generics.CreateAPIView):
  permission_classes = (AllowAny,)
  serializer_class = RegisterSerializer


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileView(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class WorkExpView(viewsets.ModelViewSet):
    queryset = WorkExp.objects.all()
    serializer_class = WorkExpSerializer


class ReviewsView(viewsets.ModelViewSet):
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer


class GetProfile(APIView):
    serializer_class = UserSerializer
    lookup_url_kwarg = 'username'

    def get(self, request, format=None):
        username = request.GET.get(self.lookup_url_kwarg)
        if username != None:
            profile = User.objects.filter(username=username)
            if len(profile) > 0:
                data = UserSerializer(profile[0]).data
                data['is_username'] = self.request.session.session_key == profile[0].username
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Profile Not Found': 'Invalid username.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'Bad Request': 'Code paramater not found in request'}, status=status.HTTP_400_BAD_REQUEST)
