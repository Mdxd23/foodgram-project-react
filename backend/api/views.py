from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from recipes.models import Favorite, Ingredient, Tag, Recipe
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from djoser.views import UserViewSet
from users.models import User, Subscription

from .serializers import (IngredientSerializer, TagSerializer,
                          RecipeShowSerializer, RecipeCreateUpdateSerializer,
                          CustomUserSerializer, ShortRecipeShowSerializer)


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

    @action(
            methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=(IsAuthenticated,)
    )
    def favorite_recipe(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = RecipeCreateUpdateSerializer()

        if request.method == 'POST':
            serializer.add_to_favorites(user, recipe)
            serializer = ShortRecipeShowSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            instance = Favorite.objects.filter(
                user=user,
                recipe=recipe).first()
            if instance:
                instance.delete()
                return Response(
                    'Рецепт удален из избранного',
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                'Рецепт не находится в избранном',
                status=status.HTTP_400_BAD_REQUEST
            )


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
