from django.conf import settings
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from djoser import utils
from djoser.views import UserViewSet, TokenCreateView

# from api.filters import RecipeFilter
from api.permissions import IsOwner
from api.serializers import (IngredientSerializer, TagSerializer,
                             TokenLoginSerializer,
                             RecipeGetSerializer, RecipeCreateSerializer)
#                              UserSerializer, UserMeSerializer)

from recipes.models import (Favorite, Ingredient, Recipe, ShoppingCart,
                            Subscrption, Tag)


class CustomUserViewSet(UserViewSet):
    pass


class CustomTokenCreateView(TokenCreateView):

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED
        )


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


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwner,)
    http_method_names = ('get', 'post', 'patch', 'delete',)
    filter_backends = (DjangoFilterBackend,)
    # filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeCreateSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    permission_classes = (IsOwner,)
    http_method_names = ('post', 'delete',)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    permission_classes = (IsOwner,)
    http_method_names = ('post', 'delete',)


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscrption.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('get', 'post', 'delete',)
