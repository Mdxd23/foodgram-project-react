from django.shortcuts import render
from recipes.models import Ingredient
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .serializers import (IngredientSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
