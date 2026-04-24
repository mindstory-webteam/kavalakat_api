import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            'success':     False,
            'status_code': response.status_code,
            'message':     _msg(response.data),
            'errors':      response.data,
        }
    else:
        logger.error('Unhandled exception: %s', exc, exc_info=True)
        response = Response(
            {'success': False, 'status_code': 500, 'message': 'Internal server error.', 'errors': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return response


def _msg(data):
    if isinstance(data, dict):
        if 'detail' in data:
            return str(data['detail'])
        k = next(iter(data), None)
        if k:
            v = data[k]
            return f'{k}: {v[0]}' if isinstance(v, list) and v else 'Validation error.'
    if isinstance(data, list) and data:
        return str(data[0])
    return 'An error occurred.'
