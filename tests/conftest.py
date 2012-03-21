# import flask


def pytest_funcarg__flaskapp(request):
    return getattr(request.module, 'app', None)

