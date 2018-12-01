def is_swagger_request(request):
    return request.query_params.get('format', None) == 'openapi'
