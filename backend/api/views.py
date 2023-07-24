from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken


from api.serializers import (IngredientSerializer, TagSerializer,
                             RecipeSerializer, TokenLoginSerializer,)
#                              UserSerializer, UserMeSerializer)

from recipes.models import Ingredient, Tag

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
