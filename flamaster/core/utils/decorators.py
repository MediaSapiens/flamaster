def api_resource(bp, url, endpoint, pk_def):
    pk = pk_def.keys()[0]
    pk_type = pk_def[pk].__name__

    def wrapper(resource_class):
        resource = resource_class().as_view(endpoint)
        bp.add_url_rule(url, view_func=resource, methods=['GET', 'POST'])
        bp.add_url_rule("%s<%s:%s>" % (url, pk_type, pk),
                        view_func=resource,
                        methods=['GET', 'PUT', 'DELETE'])
    return wrapper
