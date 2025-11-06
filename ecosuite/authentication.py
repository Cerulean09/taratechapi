from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken, AccessToken, RefreshToken
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext_lazy as _
from typing import Tuple, Optional


class SupabaseUser:
    """A simple user object that represents a Supabase user from JWT token claims"""
    def __init__(self, token_payload: dict):
        self.id = token_payload.get('id')
        self.email = token_payload.get('email')
        self.fullName = token_payload.get('fullName')
        self.role = token_payload.get('role', 'user')
        self.isActive = token_payload.get('isActive', True)
        self.phoneNumber = token_payload.get('phoneNumber')
        self.assignedBrandIds = token_payload.get('assignedBrandIds', [])
        self.assignedModuleIds = token_payload.get('assignedModuleIds', [])
        self.preferences = token_payload.get('preferences', {})
        self.dateJoined = token_payload.get('dateJoined')
        self.isPendingApproval = token_payload.get('isPendingApproval', False)
        # Django framework attributes (must be snake_case)
        self.is_authenticated = True
        self.is_anonymous = False
    
    def __str__(self):
        return self.email or str(self.id)


class SupabaseJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that validates tokens without requiring Django user model.
    Extracts user information from token claims and creates a SupabaseUser object.
    """
    
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        
        # Extract user info from token claims
        user = self.get_user(validated_token)
        
        return (user, validated_token)
    
    def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        # Try AccessToken first, then RefreshToken
        for AuthToken in [AccessToken, RefreshToken]:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append(
                    {
                        "token_class": AuthToken.__name__,
                        "token_type": AuthToken.token_type,
                        "message": e.args[0],
                    }
                )

        raise InvalidToken(
            {
                "detail": _("Given token not valid for any token type"),
                "messages": messages,
            }
        )
    
    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the validated token payload.
        Creates a SupabaseUser from token claims instead of looking up Django user.
        """
        try:
            # Get token payload
            token_payload = validated_token.payload
            
            # Check if token has required claims
            if 'id' not in token_payload and 'email' not in token_payload:
                raise InvalidToken(_("Token contained no recognizable user identification"))
            
            # Create SupabaseUser from token claims
            return SupabaseUser(token_payload)
            
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))

