from rest_framework import status
from rest_framework.exceptions import APIException


class RemoteCallException(APIException):
    default_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "remote server returned non 200 response"
