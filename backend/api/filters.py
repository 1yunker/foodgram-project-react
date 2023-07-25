from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):

    is_favorited = filters.BooleanFilter()
    is_in_shopping_cart = filters.BooleanFilter()

    # name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    # genre = filters.CharFilter(field_name='genre__slug')
    # category = filters.CharFilter(field_name='category__slug')

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')
