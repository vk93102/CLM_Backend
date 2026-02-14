from drf_spectacular.extensions import OpenApiAuthenticationExtension


class StatelessJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """Teach drf-spectacular how to describe our custom JWT auth class."""

    target_class = 'authentication.jwt_auth.StatelessJWTAuthentication'
    name = 'bearerAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }
