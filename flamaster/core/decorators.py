def api_resource(bp, endpoint, pk_def):
    pk = pk_def.keys()[0]
    pk_type = pk_def[pk] and pk_def[pk].__name__ or None
    # building url from the endpoint
    url = "/{}/".format(endpoint)

    def wrapper(resource_class):
        resource = resource_class().as_view(endpoint)
        bp.add_url_rule(url, view_func=resource, methods=['GET', 'POST'])
        if pk_type is None:
            url_rule = "%s<%s>" % (url, pk)
        else:
            url_rule = "%s<%s:%s>" % (url, pk_type, pk)
        bp.add_url_rule(url_rule,
                        view_func=resource,
                        methods=['GET', 'PUT', 'DELETE'])
    return wrapper
