from django.db.models import Count, OuterRef, Subquery
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (FavoriteGetSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeGetSerializer,
                             SubscriptionsSerializer, TagSerializer)
from api.services import generate_shopping_list
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscrption, User


class CustomUserViewSet(UserViewSet):
    """Пользователи."""

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """
        Возвращает пользователей, на которых подписан текущий пользователь.
        """
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
        """Подписаться на пользователя (автора)."""
        if request.user == author:
            return Response(
                {'errors': 'Подписываться на себя запрещено!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        _, created = Subscrption.objects.get_or_create(
            user=request.user,
            following=author
        )
        if not created:
            return Response(
                {'errors': 'Подписка на данного автора уже оформлена!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = SubscriptionsSerializer(
            instance=author,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_subscribe(self, request, author):
        """Отписаться от пользователя (автора)."""
        cnt_deleted, _ = Subscrption.objects.filter(
            user=request.user,
            following=author
        ).delete()

        if cnt_deleted == 0:
            return Response(
                {'errors': 'Подписка на данного автора не оформлена!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, pk=kwargs.get('id'))
        if request.method == 'POST':
            return self.create_subscribe(request, author)
        return self.delete_subscribe(request, author)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        from_user_favorite = Favorite.objects.filter(
            recipe=OuterRef('pk'),
            user=self.request.user.id
        )
        from_shopping_cart = ShoppingCart.objects.filter(
            recipe=OuterRef('pk'),
            user=self.request.user.id
        )
        return Recipe.objects.annotate(
            is_favorited=Count(
                Subquery(from_user_favorite.values('recipe'))
            ),
            is_in_shopping_cart=Count(
                Subquery(from_shopping_cart.values('recipe'))
            )
        )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """ Скачать список покупок. """
        if not request.user.in_shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        shopping_list = generate_shopping_list(request.user)
        response = HttpResponse(
            shopping_list,
            content_type='shopping_list.txt; charset=utf-8'
        )
        return response

    def add_to(self, model, request, recipe, errors):
        """
        Добавить рецепт в список покупок или в избранное.
        Параметры:
            model: имя модели из models
            errors: текстовое сообщение об ошибке при добавлении в базу
        """
        _, created = model.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )
        if not created:
            return Response(
                {'errors': errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = FavoriteGetSerializer(
            instance=recipe, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, request, recipe, errors):
        """
        Удалить рецепт из списка покупок или из избранного.
        Параметры:
            model: имя модели из models
            errors: текстовое сообщение об ошибке при удалении из базы
        """
        cnt_deleted, _ = model.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()

        if cnt_deleted == 0:
            return Response(
                {'errors': errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, **kwargs):
        """ Список покупок. """
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        if request.method == 'POST':
            return self.add_to(
                ShoppingCart, request, recipe,
                'Данный рецепт уже есть в списке покупок!'
            )
        return self.delete_from(
            ShoppingCart, request, recipe,
            'Данного рецепта нет в списке покупок!'
        )

    @action(
        ['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, **kwargs):
        """ Избранное. """
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        if request.method == 'POST':
            return self.add_to(
                Favorite, request, recipe,
                'Данный рецепт уже есть в избранном!'
            )
        return self.delete_from(
            Favorite, request, recipe,
            'Данного рецепта нет в избранном!'
        )
