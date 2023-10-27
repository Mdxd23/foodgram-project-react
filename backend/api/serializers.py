import base64

from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import User

MAX_VALUE = 32767
MIN_VALUE = 1


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'username',
            'is_subscribed'
        )

    def get_is_subscribed(self, data):
        user = self.context.get('request').user
        return (user.is_authenticated and user.subscriber.filter(
            author=data).exists())


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, data):
        user = self.context.get('request').user
        return (user.is_authenticated and user.subscriber.filter(
            author=data).exists())

    def get_recipes_count(self, data):
        return data.recipes.count()

    def get_recipes(self, data):
        request = self.context.get('request')
        count_limit = request.GET.get('recipes_limit')
        recipe_obj = data.recipes.all()
        if count_limit:
            recipe_obj = recipe_obj[:int(count_limit)]
        return ShortRecipeShowSerializer(
            recipe_obj, many=True
        ).data


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'username',
            'password'
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurment_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class ShortRecipeShowSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurment_unit = serializers.ReadOnlyField(
        source='ingredient.measurment_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurment_unit', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE))
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'text',
            'tags',
            'ingredients',
            'cooking_time',
            'image',
        )

    def validate(self, data):
        name = data.get('name')
        text = data.get('text')
        if Recipe.objects.filter(name=name, text=text).exists():
            raise serializers.ValidationError(
                'Такой рецепт уже существует'
            )
        return data

    def validate_tags(self, data):
        if not data:
            raise serializers.ValidationError(
                {'tags': 'Нужет хотя бы один тег!'}
            )
        tags = []
        for tag in data:
            if tag in tags:
                raise serializers.ValidationError(
                    'Тэги не могут повторяться'
                )
            tags.append(tag)
        return data

    def validate_ingredients(self, data):
        if not data:
            raise serializers.ValidationError('Нужен хотя бы 1 ингредиент')
        ingredients = []
        for ingredient in data:
            if ingredient in ingredients:
                raise serializers.ValidationError(
                    'Ингридиенты не могут повторяться'
                )
            ingredients.append(ingredient)
        return data

    def to_representation(self, instance):
        return RecipeShowSerializer(
            instance,
            context={'request': self.context.get('request')}).data

    def add_to_favorites(self, user, recipe):
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                'Рецепт уже в избранном'
            )
        Favorite.objects.create(recipe=recipe, user=user)

    def add_to_shopping_cart(self, user, recipe):
        if ShoppingCart.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                'Рецепт уже в корзине'
            )
        ShoppingCart.objects.create(recipe=recipe, user=user)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipes = Recipe.objects.create(
            **validated_data,
            author=self.context.get('request').user)
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipes,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount', 1)
            )
        recipes.tags.set(tags)
        return recipes

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        instance.image = validated_data.get('image', instance.image)
        instance.tags.set(tags)
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount', 1)
            )
        super().update(instance, validated_data)
        return instance


class RecipeShowSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredient'
    )
    image = serializers.ReadOnlyField(
        source='image.url')
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        request = self.context['request']
        user = request.user
        return (user.is_authenticated and Favorite.objects.filter(
            recipe=obj, user=user).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        user = request.user
        return (user.is_authenticated and ShoppingCart.objects.filter(
            recipe=obj, user=user).exists())
