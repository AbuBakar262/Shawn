from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import User


class SigninSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        max_length=128,
        label='Password',
        style={'input_type': 'password'},
        write_only=True
    )

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError({
                    "status": "error",
                    "status_code": 400,
                    "message": "Invalid email or password"
                })
        else:
            raise serializers.ValidationError({
                "status": "error",
                "status_code": 400,
                "message": "Please provide email and password"
            })
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'gender', 'contact', 'instagram', 'dob', 'bio']
