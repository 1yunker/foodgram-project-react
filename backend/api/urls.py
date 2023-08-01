from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, RecipeViewSet,
                       TagViewSet, CustomTokenCreateView,
                       subscriptions_list,)

router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
# router.register('recipes/download_shopping_cart', , basename='download')
# router.register(
#     r'recipes/(?P<recipe_id>\d+)/favorite',
#     views.FavoriteViewSet,
#     basename='favorite')
# router.register(
#     r'recipes/(?P<recipe_id>\d+)/shopping_cart',
#     views.ShoppingCartViewSet,
#     basename='shopping_cart')
router.register(
    'users/subscriptions',
    subscriptions_list,
    basename='subscriptions')
# router.register(
#     'users/(?P<user_id>\d+)/subscribe',
#     SubscriptionViewSet,
#     basename='subscriptions')


urlpatterns = [
    path('', include(router.urls), name='api-root'),
    path('', include('djoser.urls')),
    path('auth/token/login/', CustomTokenCreateView.as_view(), name='login'),
    path('auth/', include('djoser.urls.authtoken')),
]
