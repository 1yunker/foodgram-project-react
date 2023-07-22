from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register('ingredients', views.IngredientViewSet, basename='ingredients')
router.register('tags', views.TagViewSet, basename='tags')
router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    views.FavoriteViewSet,
    basename='favorite')
router.register('users', views.UserViewSet, basename='users')

auth_patterns = [
    path('token/login/', views.obtain_token, name='login'),
    path('token/logout/', views.delete_token, name='logout'),
]

urlpatterns = [
    path('auth/', include(auth_patterns)),
    path('', include(router.urls), name='api-root')
]
