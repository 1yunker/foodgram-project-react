from django_filters.rest_framework import (AllValuesMultipleFilter,
                                           BooleanFilter, FilterSet)
from recipes.models import Recipe


class RecipeFilter(FilterSet):

    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    def get_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(who_likes__id=self.request.user.id)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(who_buys__id=self.request.user.id)

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')
