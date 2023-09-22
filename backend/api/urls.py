from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import IngredientViewSet


app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls))
]
