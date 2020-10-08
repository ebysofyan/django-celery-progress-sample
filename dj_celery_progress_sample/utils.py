import pandas as pd
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class DataframeUtil(object):
    @staticmethod
    def get_validated_dataframe(path: str) -> pd.DataFrame:
        df = pd.read_excel(path, dtype=str)
        df.columns = df.columns.str.lower()
        df = df.fillna(-1)
        return df.mask(df == -1, None)


def in_memory_file_to_temp(in_memory_file):
    path = default_storage.save('tmp/%s' % in_memory_file.name, ContentFile(in_memory_file.read()))
    return path
