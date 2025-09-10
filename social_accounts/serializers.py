from rest_framework import serializers
from .utils import GoogleSocialAuth,register_social_user
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class GoogleSignInSerializer(serializers.Serializer):
    access_token=serializers.CharField(min_length=6)
    def validate_access_token(self,access_token):
        google_user_data=GoogleSocialAuth.validate(access_token)
        try:
            guserid=google_user_data['sub']
        except:
            raise serializers.ValidationError("this token is invalid or expired")
        if google_user_data['aud']!= settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed(detail="could not verify user")
        email=google_user_data['email']
        first_name=google_user_data['given_name']
        last_name=google_user_data['family_name']
        provider='google'
        return register_social_user(provider, email, first_name, last_name)