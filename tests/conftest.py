# import flask
import os
os.environ['TESTING'] = 'True'


def pytest_funcarg__flaskapp(request):
    return getattr(request.module, 'app', None)

