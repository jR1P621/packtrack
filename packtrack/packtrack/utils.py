from __future__ import unicode_literals
from django.db import IntegrityError
from rest_framework.views import Response, exception_handler
from rest_framework import status


def custom_exception_handler(e, context):
    # Call REST framework's default exception handler first to get the standard error response.
    response = exception_handler(e, context)

    # if there is an IntegrityError and the error response hasn't already been generated
    if isinstance(e, Exception) and not response:
        response = Response(
            {
                'message': f'{type(e).__name__}: {e}'
                # Could not perform action. Form data may be incorrect '
                # 'or a duplicate object may already exists.'
            },
            status=status.HTTP_400_BAD_REQUEST)

    return response
