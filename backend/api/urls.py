from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, RecipeViewSet,
                       TagViewSet, CustomTokenCreateView,
                       CustomUserViewSet)

router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', CustomUserViewSet, basename='users')
# router.register(
#     r'recipes/(?P<recipe_id>\d+)/favorite',
#     views.FavoriteViewSet,
#     basename='favorite')
# router.register(
#     r'recipes/(?P<recipe_id>\d+)/shopping_cart',
#     views.ShoppingCartViewSet,
#     basename='shopping_cart')


urlpatterns = [
    path('', include(router.urls), name='api-root'),
    path('', include('djoser.urls')),
    path('auth/token/login/', CustomTokenCreateView.as_view(), name='login'),
    path('auth/', include('djoser.urls.authtoken')),
]
