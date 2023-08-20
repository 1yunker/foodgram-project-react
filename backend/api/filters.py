from django_filters.rest_framework import (AllValuesMultipleFilter,
                                           BooleanFilter, FilterSet)
from recipes.models import Recipe


class RecipeFilter(FilterSet):

    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    def filter_by_user(self, queryset, name, value, related_name_id):
        if not value:
            return queryset
        if self.request.user.is_authenticated:
            return queryset.filter(**{related_name_id: self.request.user.id})
        return Recipe.objects.none()

    def get_is_favorited(self, queryset, name, value):
        return self.filter_by_user(queryset, name, value, 'who_likes__id')

    def get_is_in_shopping_cart(self, queryset, name, value):
        return self.filter_by_user(queryset, name, value, 'who_buys__id')

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')
