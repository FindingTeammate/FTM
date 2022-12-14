import email
import os
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.utils.module_loading import import_string
from rest_framework import generics, status
from .models import Profile, WorkExp, Reviews
from .serializer import ProfileSerializer, WorkExpSerializer, ReviewsSerializer, UserSerializer, RegisterSerializer, \
    MyTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, DjangoModelPermissions
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from friendship.models import Friend, FriendshipRequest
from friendship.exceptions import AlreadyExistsError, AlreadyFriendsError
from .serializer import FriendshipRequestSerializer, FriendSerializer, FriendshipRequestResponseSerializer, ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer
from django.conf import settings
from rest_framework_simplejwt.models import TokenUser
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from .utils import Util


# class UserDetailAPI(APIView):
#   authentication_classes = (TokenAuthentication,)
#   permission_classes = (AllowAny,)
#   def get(self,request,*args,**kwargs):
#     user = User.objects.get(id=request.user.id)
#     serializer = UserSerializer(user)
#     return Response(serializer.data)


class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterUserAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileView(viewsets.ModelViewSet):
    # permission_classes = [DjangoModelPermissions]
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

    
User = get_user_model()

REST_FRIENDSHIP = getattr(settings, "REST_FRIENDSHIP", None)


class FriendViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Friend model
    """
    permission_classes = [AllowAny]
    serializer_class = FriendSerializer
    lookup_field = 'pk'

    def get_queryset(self, *args, **kwargs):
        queryset = User.objects.all()
        return queryset

    def list(self, request):
        friend_requests = Friend.objects.friends(user=request.user)
        self.queryset = friend_requests
        self.http_method_names = ['get', 'head', 'options', ]
        return Response(FriendSerializer(friend_requests, many=True).data)

    def retrieve(self, request, pk=None):
        self.queryset = Friend.objects.friends(user=request.user)
        requested_user = get_object_or_404(User, pk=pk)
        if Friend.objects.are_friends(request.user, requested_user):
            self.http_method_names = ['get', 'head', 'options', ]
            return Response(FriendSerializer(requested_user, many=False).data)
        else:
            return Response(
                {'message': "Friend relationship not found for user."},
                status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False)
    def requests(self, request):
        friend_requests = Friend.objects.unrejected_requests(user=request.user)
        self.queryset = friend_requests
        return Response(
            FriendshipRequestSerializer(friend_requests, many=True).data)

    @action(detail=False)
    def sent_requests(self, request):
        friend_requests = Friend.objects.sent_requests(user=request.user)
        self.queryset = friend_requests
        return Response(
            FriendshipRequestSerializer(friend_requests, many=True).data)

    @action(detail=False)
    def rejected_requests(self, request):
        friend_requests = Friend.objects.rejected_requests(user=request.user)
        self.queryset = friend_requests
        return Response(
            FriendshipRequestSerializer(friend_requests, many=True).data)

    @action(detail=False,
            serializer_class=FriendshipRequestSerializer,
            methods=['post'])
    def add_friend(self, request, username=None):
        """
        Add a new friend with POST data
        - to_user
        - message
        """
        # Creates a friend request from POST data:
        # - username
        # - message
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        to_user = get_object_or_404(
            User,
            username=serializer.validated_data.get('to_user')
        )

        try:
            friend_obj = Friend.objects.add_friend(
                # The sender
                request.user,
                # The recipient
                to_user,
                # Message (...or empty str)
                message=request.data.get('message', '')
            )
            return Response(
                FriendshipRequestSerializer(friend_obj).data,
                status.HTTP_201_CREATED
            )
        except (AlreadyExistsError, AlreadyFriendsError) as e:
            return Response(
                {"message": str(e)},
                status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, serializer_class=FriendshipRequestSerializer, methods=['post'])
    def remove_friend(self, request):
        """
        Deletes a friend relationship.
        The username specified in the POST data will be
        removed from the current user's friends.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        to_user = get_object_or_404(
            User,
            username=serializer.validated_data.get('to_user')
        )

        if Friend.objects.remove_friend(request.user, to_user):
            message = 'Friend deleted.'
            status_code = status.HTTP_204_NO_CONTENT
        else:
            message = 'Friend not found.'
            status_code = status.HTTP_400_BAD_REQUEST

        return Response(
            {"message": message},
            status=status_code
        )

    @action(detail=False,
            serializer_class=FriendshipRequestResponseSerializer,
            methods=['post'])
    def accept_request(self, request, id=None):
        """
        Accepts a friend request
        The request id specified in the URL will be accepted
        """
        id = request.data.get('id', None)
        friendship_request = get_object_or_404(
            FriendshipRequest, pk=id)

        if not friendship_request.to_user == request.user:
            return Response(
                {"message": "Request for current user not found."},
                status.HTTP_400_BAD_REQUEST
            )

        friendship_request.accept()
        return Response(
            {"message": "Request accepted, user added to friends."},
            status.HTTP_201_CREATED
        )

    @action(detail=False,
            serializer_class=FriendshipRequestResponseSerializer,
            methods=['post'])
    def reject_request(self, request, id=None):
        """
        Rejects a friend request
        The request id specified in the URL will be rejected
        """
        id = request.data.get('id', None)
        friendship_request = get_object_or_404(
            FriendshipRequest, pk=id)
        if not friendship_request.to_user == request.user:
            return Response(
                {"message": "Request for current user not found."},
                status.HTTP_400_BAD_REQUEST
            )

        friendship_request.reject()

        return Response(
            {
                "message": "Request rejected, user NOT added to friends."
            },
            status.HTTP_201_CREATED
        )

class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    queryset = User.objects.filter(email= email)
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            redirect_url = request.data.get('redirect_url', '')
            absurl = 'http://'+current_site + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + \
                absurl+"?redirect_url="+redirect_url
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            Util.send_email(data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'})

            return Response({'success': True, 'message': 'Credentials Valid', 'uidb64':uidb64, 'token':token})

        except DjangoUnicodeDecodeError as identifier:
            if not PasswordResetTokenGenerator().check_token(user,token):
                return Response({'error': 'Token is not valid, please request a new one'})


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)
