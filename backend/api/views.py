from django.db import IntegrityError
# from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework import filters, mixins
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from djoser import utils
from djoser.conf import settings
from djoser.views import UserViewSet, TokenCreateView

from api.filters import RecipeFilter
from api.permissions import IsOwner
from api.serializers import (IngredientSerializer, TagSerializer,
                             RecipeGetSerializer, RecipeCreateSerializer,
                             SubscriptionsSerializer, FavoriteGetSerializer,)

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscrption, User


class CustomUserViewSet(UserViewSet):
    '''Пользователи'''
    # pagination_class = LimitPageNumberPagination

    @action(['GET'], detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        '''Мои подписки'''
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionsSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionsSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_subscribe(self, request, author):
        '''Подписаться на пользователя'''
        if request.user == author:
            return Response(
                {'errors': 'Подписываться на себя запрещено!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            Subscrption.objects.create(user=request.user, following=author)
        except IntegrityError:
            return Response(
                {'errors': 'Подписка на данного автора уже оформлена!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = SubscriptionsSerializer(
            instance=author, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_subscribe(self, request, author):
        '''Отписаться от пользователя'''
        try:
            Subscrption.objects.get(
                user=request.user, following=author).delete()
        except Subscrption.DoesNotExist:
            return Response(
                {'errors': 'Подписка на данного автора не оформлена!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(['POST', 'DELETE'], detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        try:
            author = get_object_or_404(User, pk=kwargs.get('id'))
        except Http404:
            return Response(
                {'detail': 'Страница не найдена.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.method == 'POST':
            return self.create_subscribe(request, author)
        return self.delete_subscribe(request, author)


class CustomTokenCreateView(TokenCreateView):
    '''Получить токен авторизации'''
    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ('get',)
    pagination_class = None
    search_fields = ('name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ('get',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwner,)
    http_method_names = ('get', 'post', 'patch', 'delete',)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(['GET'], detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        '''Скачать список покупок'''
        pass

    def add_to_shopping_cart(self, request, recipe):
        '''Добавить рецепт в список покупок'''
        try:
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
        except IntegrityError:
            return Response(
                {'errors': 'Данный рецепт уже есть в списке покупок!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = FavoriteGetSerializer(
            instance=recipe, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from_shopping_cart(self, request, recipe):
        '''Удалить рецепт из списка покупок'''
        try:
            ShoppingCart.objects.get(
                user=request.user, recipe=recipe).delete()
        except ShoppingCart.DoesNotExist:
            return Response(
                {'errors': 'Данного рецепта нет в списке покупок!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(['POST', 'DELETE'], detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        try:
            recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        except Http404:
            return Response(
                {'detail': 'Страница не найдена.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.method == 'POST':
            return self.add_to_shopping_cart(request, recipe)
        return self.delete_from_shopping_cart(request, recipe)

    def add_to_favorite(self, request, recipe):
        '''Добавить рецепт в избранное'''
        try:
            Favorite.objects.create(user=request.user, recipe=recipe)
        except IntegrityError:
            return Response(
                {'errors': 'Данный рецепт уже есть в избранном!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = FavoriteGetSerializer(
            instance=recipe, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from_favorite(self, request, recipe):
        '''Удалить рецепт из избранного'''
        try:
            Favorite.objects.get(
                user=request.user, recipe=recipe).delete()
        except ShoppingCart.DoesNotExist:
            return Response(
                {'errors': 'Данного рецепта нет в избранном!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(['POST', 'DELETE'], detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, **kwargs):
        try:
            recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        except Http404:
            return Response(
                {'detail': 'Страница не найдена.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.method == 'POST':
            return self.add_to_favorite(request, recipe)
        return self.delete_from_favorite(request, recipe)
