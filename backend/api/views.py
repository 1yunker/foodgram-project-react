from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken


# from api.serializers import (IngredientSerializer, TagSerializer,
#                              RecipeSerializer, TokenLoginSerializer,
#                              UserSerializer, UserMeSerializer)
from api.serializers import TokenLoginSerializer
# from reviews.models import Category, Genre, Review, Title

User = get_user_model()


@api_view(['POST'])
def obtain_token(request):
    serializer = TokenLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    password = serializer.validated_data.get('password')
    email = serializer.validated_data.get('email')
    user = get_object_or_404(User, password=password, email=email)
    token = AccessToken.for_user(user)
    return Response({'auth_token': str(token)}, status.HTTP_201_CREATED)
