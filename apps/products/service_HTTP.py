import csv
import yaml
from yaml import Loader

from rest_framework.exceptions import ValidationError


from apps.products import service


def import_data(name_file, data_format, owner_id):
    if data_format not in service.SUPPORTED_DATA_FORMATS:
        raise NotImplementedError(
            f"{data_format} not supported. Available only: {service.SUPPORTED_DATA_FORMATS.keys()}"
        )

    if data_format == "csv":
        with open(f"data_all/{name_file}.{data_format}", "r", encoding="utf-8") as fd:
            data_stream_csv = list(csv.DictReader(fd))

        service.load_data_csv(data_stream_csv, owner_id)

    else:
        with open(f"data_all/{name_file}.{data_format}", "r", encoding="utf-8") as fd:
            data_stream_yaml = yaml.load(fd, Loader=Loader)
        service.load_data_yml(data_stream_yaml, owner_id)
