from rest_framework import serializers
from recipes.models import Ingredient
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')
