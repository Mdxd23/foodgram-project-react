from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (IngredientViewSet, TagViewSet, RecipeViewSet,
                       CustomUserViewSet)


app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

]
