from rest_framework import serializers
from recipes.models import (Ingredient, Tag, Recipe, TagInRecipe,
                            IngredientInRecipe, Favorite)
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


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ('__all__')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurment_unit = serializers.ReadOnlyField(
        source='ingredient.measurment_unit'
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
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Нужет хотя бы один тег!'}
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('tags', 'Теги не уникальны!')
        return data

    def validate_ingredients(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError('Нужен хотя бы 1 ингредиент')

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipes = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            current_ingredient = ingredient.get('ingredients')
            current_amount = ingredient.get('amount')
            IngredientInRecipe.objects.create(
                recipe=recipes,
                ingredient=current_ingredient,
                amount=current_amount
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


class RecipeShowSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients',
    )
    image = Base64ImageField()
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    author = serializers.CurrentUserDefault()
    is_favorite = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('__all__')

    def get_is_favorite(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Favorite.objects.filter(recipe=obj, user=user).exists()
        return False

    def get_ingredients(self, recipe):
        ingredients = IngredientInRecipe.objects.filter(recipe=recipe)
        return IngredientAmountSerializer(ingredients).data
