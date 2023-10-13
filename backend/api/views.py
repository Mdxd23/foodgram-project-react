from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, Tag, Recipe
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from djoser.views import UserViewSet
from users.models import User, Subscription

from .serializers import (IngredientSerializer, TagSerializer,
                          RecipeShowSerializer, RecipeCreateUpdateSerializer,
                          CustomUserSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    #permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action == 'GET':
            return RecipeShowSerializer
        return RecipeCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
