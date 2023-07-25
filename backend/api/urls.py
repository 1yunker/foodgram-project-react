from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register('ingredients', views.IngredientViewSet, basename='ingredients')
router.register('tags', views.TagViewSet, basename='tags')
router.register('recipes', views.RecipeViewSet, basename='recipes')
# router.register('recipes/download_shopping_cart', , basename='download')
# router.register(
#     r'recipes/(?P<recipe_id>\d+)/favorite',
#     views.FavoriteViewSet,
#     basename='favorite')
# router.register(
#     r'recipes/(?P<recipe_id>\d+)/shopping_cart',
#     views.ShoppingCartViewSet,
#     basename='shopping_cart')
#  router.register('users', views.CustomUserViewSet, basename='users')
#  router.register('users/subscriptions', views.SubscriptionViewSet, basename='subscriptions')


urlpatterns = [
    path('', include(router.urls), name='api-root'),
    path('auth/', include('djoser.urls')),
    path('auth/token/login/', views.CustomTokenCreateView.as_view(), name='login'),
    path('auth/', include('djoser.urls.authtoken')),
]
