from unittest.mock import Mock
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from api.serializers import UserSerializer


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }


class CustomJwtAuthentication(JSONWebTokenAuthentication):
    def authenticate_credentials(self, payload):
        if 'internal' in payload:
            return Mock(is_authenticated=True)
        else:
            return super().authenticate_credentials(payload)
