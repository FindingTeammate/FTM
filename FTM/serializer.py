from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, WorkExp, Reviews
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from friendship.models import FriendshipRequest
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


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

