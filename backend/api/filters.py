from django_filters.rest_framework import (AllValuesMultipleFilter,
                                           BooleanFilter,
                                           CharFilter,
                                           FilterSet)

from recipes.models import Recipe, Ingredient


class RecipeFilter(FilterSet):

    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    def get_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        # добываем все записи из Favorite по текущему пользователю
        favorites = self.request.user.in_favorites.all()
        return queryset.filter(
            pk__in=(favorite.recipe.pk for favorite in favorites)
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        # добываем все записи из ShoppingCart по текущему пользователю
        shopping_cart = self.request.user.in_shopping_cart.all()
        return queryset.filter(
            pk__in=(item.recipe.pk for item in shopping_cart)
        )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')


class IngredientSearchFilter(FilterSet):
    # name = CharFilter(field_name='name', lookup_expr='istartswith')

    name = CharFilter(method='search_by_name')

    def search_by_name(self, queryset, name, value):
        if not value:
            return queryset
        startswith_queryset = (
            queryset.filter(name__istartswith=value).annotate(order=0))
        contains_queryset = (
            queryset.filter(name__icontains=value).exclude(
                pk__in=(ingredient.pk for ingredient in startswith_queryset)
            ).annotate(order=1)
        )
        return startswith_queryset.union(contains_queryset).order_by('order')

    class Meta:
        model = Ingredient
        fields = ('name',)
