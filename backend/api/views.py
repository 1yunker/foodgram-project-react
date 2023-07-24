from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from djoser.views import UserViewSet

from api.serializers import (IngredientSerializer, TagSerializer,
                             TokenLoginSerializer,)
#                              RecipeSerializer, )
#                              UserSerializer, UserMeSerializer)

from recipes.models import Ingredient, Tag


class CustomUserViewSet(UserViewSet):
    pass


@api_view(['POST'])
def obtain_token(request):
    serializer = TokenLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    password = serializer.validated_data.get('password')
    email = serializer.validated_data.get('email')
    user = get_object_or_404(
        settings.AUTH_USER_MODEL,
        password=password, email=email
    )
    token = AccessToken.for_user(user)
    return Response({'auth_token': str(token)}, status.HTTP_201_CREATED)


class IngredientTagViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           mixins.ListModelMixin, viewsets.GenericViewSet):
    lookup_field = 'slug'
    # permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class IngredientViewSet(IngredientTagViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(IngredientTagViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
