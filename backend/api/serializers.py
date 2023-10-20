import base64
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from rest_framework import serializers
from djoser.serializers import UserSerializer, UserCreateSerializer
from recipes.models import (Ingredient, Tag, Recipe,
                            IngredientInRecipe, Favorite)
from users.models import User, Subscription


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('__all__')

    def get_is_subscribed(self, data):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.subscriber.filter(author=data).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('__all__')


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


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')

    def __str__(self):
        return f'{self.id} {self.amount}'


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
        validators=[MinValueValidator(1)]
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    author = serializers.CurrentUserDefault()

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

    def validate_tags(self, data):
        if not data:
            raise serializers.ValidationError(
                {'tags': 'Нужет хотя бы один тег!'}
            )
        if len(data) != len(set(data)):
            raise serializers.ValidationError('tags', 'Теги не уникальны!')
        return data

    def validate_ingredients(self, data):
        if not data:
            raise serializers.ValidationError('Нужен хотя бы 1 ингредиент')
        return data

    def to_representation(self, instance):
        serializer = RecipeShowSerializer(
            instance,
            context=self.context
        )
        return serializer.data

    def add_to_favorites(self, user, recipe):
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                'Рецепт уже в избранном'
            )
        Favorite.objects.create(recipe=recipe, user=user)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipes = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipes,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        recipes.tags.set(tags)
        return recipes

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        instance.image = validated_data.get('image', instance.image)
        instance.tags.set(tags)
        instance.save
        return instance


class RecipeShowSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredient',
    )
    image = Base64ImageField()
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    author = CustomUserSerializer(read_only=True)
    is_favorite = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('__all__')

    def get_is_favorite(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Favorite.objects.filter(recipe=obj, user=user).exists()
        return False
