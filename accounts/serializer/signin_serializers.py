from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import User


class SigninSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        max_length=128,
        label='Password',
        style={'input_type': 'password'},
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError({'email': 'Invalid Credentials'})
        else:
            raise serializers.ValidationError({'email': 'Email and Password are required'})
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'gender'
                                                                        'contact', 'instagram', 'dob', 'bio']
