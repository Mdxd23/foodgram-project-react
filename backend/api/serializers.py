from rest_framework import serializers
from recipes.models import (Ingredient, Tag, Recipe, TagInRecipe,
                            IngredientInRecipe)
from users.models import User
from drf_extra_fields.fields import Base64ImageField


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientM2MSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'ingredient',
            'amount',
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientM2MSerializer(
        many=True,
        source='ingredient'
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()
    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        slug_field='id'
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

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipes = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            current_ingredient = ingredient.get('ingredients')
            amount = ingredient.get('amount')
            IngredientInRecipe.objects.create(
                recipe=recipes,
                ingredient=current_ingredient,
                amount=amount
            )
        recipes.tags.set(tags)
        return recipes

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for ingredient in ingredients:
            current_ingredient = ingredient.get('ingredients')
            amount = ingredient.get('amount')
            IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient=current_ingredient,
                amount=amount
            )
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        TagInRecipe.objects.filter(recipe=instance).delete()
        instance.image = validated_data.get('image', instance.image)
        instance.tags.set(tags)
        instance.save
        return instance


class RecipeIngredientsReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurment_unit = serializers.ReadOnlyField(
        source='ingredient.measurment_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('__all__')


class RecipeShowSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientsReadSerializer(
        many=True,
        read_only=True
    )
    image = Base64ImageField()
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    author = serializers.CurrentUserDefault

    class Meta:
        model = Recipe
        fields = ('__all__')

    def get_ingredients(self, recipe):
        ingredients = IngredientInRecipe.objects.filter(recipe=recipe)
        return RecipeIngredientsReadSerializer(ingredients).data
