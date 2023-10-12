from rest_framework import serializers
from djoser.serializers import UserSerializer
from recipes.models import (Ingredient, Tag, Recipe,
                            IngredientInRecipe, Favorite)
from users.models import User
from drf_extra_fields.fields import Base64ImageField


class CustomUserSerializer(UserSerializer):

    class Meta:
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ('__all__')

    def __str__(self):
        return f'{self.id} {self.amount}'


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurment_unit = serializers.ReadOnlyField(
        source='ingredients.measurment_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('__all__')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()
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
        instance.name = validated_data['name']
        instance.text = validated_data['text']
        instance.cooking_time = validated_data['cooking_time']
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        instance.image = validated_data['image']
        instance.tags.set(tags)
        instance.save
        return instance

    def to_representation(self, instance):
        serializer = RecipeShowSerializer(
            instance,
            context=self.context
        )
        return serializer.data


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
    


