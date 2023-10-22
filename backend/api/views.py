from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
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
                          CustomUserSerializer, ShortRecipeShowSerializer,
                          SubscriptionSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
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
        user = request.user
        ingredient_name = 'recipe__recipe_ingredient__ingredient__name'
        unit = 'recipe__recipe_ingredient__ingredient__measurment_unit'
        amount = 'recipe__recipe_ingredient__amount'
        items = ShoppingCart.objects.filter(user=user).values(
            ingredient_name,
            unit
        ).annotate(amount=Sum(amount))
        shopping_cart = []

        for item in items:
            name = item[ingredient_name]
            amount = item['amount']
            measurment_unit = item[unit]

            shopping_cart.append(f'{name} - {amount} {measurment_unit}')

        file_name = 'shopping_cart.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(
            detail=False,
            methods=['GET']
    )
    def subscriptions(self, request):
        user = request.user
        queryset = self.paginate_queryset(
            User.objects.filter(subscription__subscriber=user)
        )
        serializer = SubscriptionSerializer(
            queryset,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(
            methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, *args, **kwargs):
        subscriber = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)

        if subscriber == author:
            return Response(
                'Нельзя подписаться на себя',
                status=status.HTTP_400_BAD_REQUEST
            )

        instance = Subscription.objects.filter(
            subscriber=subscriber,
            author=author
        )

        if request.method == 'POST':
            if instance.exists():
                return Response(
                    'Пользователь уже подписан на автора',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(subscriber=subscriber, author=author)
            serializer = SubscriptionSerializer(
                author,
                context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if instance.exists():
                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                'Пользователь не подписан на автора',
                status=status.HTTP_400_BAD_REQUEST
            )
