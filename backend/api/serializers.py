from rest_framework import serializers
from recipes.models import (Ingredient, Tag, Recipe, TagInRecipe,
                            IngredientInRecipe)
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')
