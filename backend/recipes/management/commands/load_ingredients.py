import os
from csv import reader

from django.core.management import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(
            os.path.join(
                os.path.join(BASE_DIR, 'recipes/data'), 'ingredients.csv'
            ),
                'r',
                encoding='utf-8'
        ) as file:
            csv_reader = reader(file, delimiter=',')
            for row in csv_reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurment_unit=row[1]
                )
        print('Done loading ing')
