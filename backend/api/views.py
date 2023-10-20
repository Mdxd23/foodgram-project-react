from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from recipes.models import Favorite, Ingredient, Tag, Recipe, ShoppingCart
from rest_framework import viewsets, status, serializers
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
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = RecipeCreateUpdateSerializer()

        if request.method == 'POST':
            try:
                serializer.add_to_favorites(user, recipe)
                serializer = ShortRecipeShowSerializer(recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            except serializers.ValidationError as error:
                return Response(str(error), status=status.HTTP_400_BAD_REQUEST)

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

    @action(
            methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = RecipeCreateUpdateSerializer()

        if request.method == 'POST':
            try:
                serializer.add_to_shopping_cart(user, recipe)
                serializer = ShortRecipeShowSerializer(recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            except serializers.ValidationError as error:
                return Response(str(error), status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            instance = ShoppingCart.objects.filter(
                user=user,
                recipe=recipe).first()
            if instance:
                instance.delete()
                return Response(
                    'Рецепт удален из корзины',
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                'Рецепт не находится в корзине',
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
            detail=False,
            permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        recipes = Recipe.objects.filter(
            shopping_cart__user=request.user
        ).prefetch_related('recipe_ingredient__ingredient')
        ingredients = {}
        for recipe in recipes:
            for recipe_ingredient in recipe.recipe_ingredient.all():
                name = recipe_ingredient.ingredient.name
                amount = recipe_ingredient.amount
                measurment_unit = recipe_ingredient.ingredient.measurment_unit
                if name in ingredients:
                    ingredients[name]['amount'] += amount
                else:
                    ingredients[name] = {
                        'amount': amount,
                        'measurment_unit': measurment_unit
                    }
        file_data = ''
        for name, details in ingredients.items():
            file_data += (
                f'{name}: {details["amount"]} {details["measurment_unit"]}')
        return HttpResponse(file_data, content_type='text/plain')


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
