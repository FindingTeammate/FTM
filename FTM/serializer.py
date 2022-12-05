from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, WorkExp, Reviews
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from friendship.models import FriendshipRequest
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str
from .utils import Util
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import AuthenticationFailed

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        print(attrs)
        data = super().validate(attrs)
        token = self.get_token(self.user)
        data['id'] = self.user.id
        data['user'] = str(self.user)
        return data



class RegisterSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(
    required=True,
    validators=[UniqueValidator(queryset=User.objects.all())]
  )
  password = serializers.CharField(
    write_only=True, required=True, validators=[validate_password])
  password2 = serializers.CharField(write_only=True, required=True)
  tokens = serializers.SerializerMethodField()
  class Meta:
    model = User
    fields = ('id','username', 'password', 'password2',
         'email', 'first_name', 'last_name', 'tokens')
    extra_kwargs = {
      'first_name': {'required': True},
      'last_name': {'required': True}
    }

  def get_tokens(self, user):
      tokens = RefreshToken.for_user(user)
      refresh = str(tokens)
      access = str(tokens.access_token)
      data = {
          "refresh": refresh,
          "access": access
      }
      return data

  def validate(self, attrs):
    if attrs['password'] != attrs['password2']:
      raise serializers.ValidationError(
        {"password": "Password fields didn't match."})
    return attrs
  def create(self, validated_data):
    user = User.objects.create(
      username=validated_data['username'],
      email=validated_data['email'],
      first_name=validated_data['first_name'],
      last_name=validated_data['last_name'],
    )
    user.set_password(validated_data['password'])
    user.save()
    return user


class WorkExpSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExp
        fields = "__all__"

class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ('id', 'user', 'comments', 'ratings', 'endorsements')


class ProfileSerializer(serializers.ModelSerializer):
    review = ReviewsSerializer(read_only=True, many=True)
    exp = WorkExpSerializer(read_only=True, many=True)
    class Meta:
        model = Profile
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True, many=False)
    class Meta:
        model = User
        fields = "__all__"


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username','first_name','last_name', 'email')


class FriendshipRequestSerializer(serializers.ModelSerializer):
    to_user = serializers.CharField()
    from_user = serializers.StringRelatedField()

    class Meta:
        model = FriendshipRequest
        fields = ('id', 'from_user', 'to_user', 'message',
                  'created', 'rejected', 'viewed')
        extra_kwargs = {
            'from_user': {'read_only': True},
            'created': {'read_only': True},
            'rejected': {'read_only': True},
            'viewed': {'read_only': True},
        }


class FriendshipRequestResponseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = FriendshipRequest
        fields = ('id',)


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
            import pdb
            pdb.set_trace()
            email = attrs['data'].get('email','')


            return super().validate(attrs)


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=8, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)
