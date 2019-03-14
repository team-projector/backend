# SWAGGER_SETTINGS = {
#     'USE_SESSION_AUTH': False,
#     'SECURITY_DEFINITIONS': {
#         'api_key': {
#             'type': 'apiKey',
#             'description': 'Token authorization',
#             'name': 'Authorization',
#             'in': 'header'
#         }
#     },
#     'LOGIN_URL': None,
#     'LOGOUT_URL': None,
#     'DOC_EXPANSION': None,
#     'APIS_SORTER': None,
#     'OPERATIONS_SORTER': None,
#     'JSON_EDITOR': True,
#     'SHOW_REQUEST_HEADERS': False,
#     'SUPPORTED_SUBMIT_METHODS': [
#         'get',
#         'post',
#         'put',
#         'delete',
#         'patch'
#     ],
#     'VALIDATOR_URL': '',
# }
#


SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': True,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}
