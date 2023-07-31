import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Measurement


TABLES = {
    Ingredient: 'ingredients.csv',
}


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for model, csv_f in TABLES.items():
            with open(
                # f'{settings.BASE_DIR}\\data\\{csv_f}',
                f'{settings.BASE_DIR}/data/{csv_f}',
                newline='',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.reader(csv_file)
                data = []
                for row in reader:
                    m_unit, _ = Measurement.objects.get_or_create(name=row[1])
                    data.append(model(name=row[0].capitalize(),
                                      measurement_unit=m_unit))
            model.objects.bulk_create(data)
        self.stdout.write(self.style.SUCCESS('Данные успешно загружены!'))
