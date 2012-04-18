from flamaster.app import app


@app.template_filter('rstrip')
def rstrip(value, string):
    """ filter that brings standart string.rstrip method functionality into
        template context
    """
    return value.rstrip(string)
