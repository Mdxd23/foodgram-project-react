from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import IngredientViewSet, TagViewSet, RecipeViewSet


app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

]
