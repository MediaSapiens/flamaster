import os
from werkzeug import secure_filename


def create_name(filename):
    filename = secure_filename(filename)
    name = os.path.splitext(filename)[0]
    return name


def filter_wrapper(criterion):
    def transform(q):
        return q.filter(criterion)
    return transform


class DictObj(dict):
    def __getattr__(self, value):
        return self[value]

    def __setattr__(self, key, value):
        self[key] = value


dict_obj = DictObj
