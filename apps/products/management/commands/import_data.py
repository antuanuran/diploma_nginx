import os.path

from django.core.management import BaseCommand

from apps.products.service import import_data


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")
        parser.add_argument("--owner_id")

    def handle(self, path: str, *args, **options):
        data_format = os.path.splitext(os.path.basename(path))[-1][1:]

        with open(path, "r") as file:
            import_data(file, data_format, options["owner_id"])
