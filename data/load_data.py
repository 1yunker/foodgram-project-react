import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from backend.recipes.models import Ingredient, Measurement


TABLES = {
    Ingredient: 'ingredients.csv',
}


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for model, csv_f in TABLES.items():
            with open(
                f'{settings.BASE_DIR}/data/{csv_f}',
                'r',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                data = []
                for row in reader:
                    m_str = row[1]
                    m_unit = Measurement.objects.get_or_create(name=m_str)
                    data.append(model(row[0], m_unit))
                    # data.append(model(**row))
            model.objects.bulk_create(data)
