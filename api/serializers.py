from rest_framework import serializers
from django.contrib.auth.models import User

from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    def validate_password(self, value: str) -> str:
        hashed_password = make_password(value)
        return hashed_password

    def update(self, instance: User, validated_data: dict) -> User:
        instance.email = validated_data.get("email", instance.email)
        instance.password = validated_data.get("password", instance.password)
        instance.username = validated_data.get("username", instance.username)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = "__all__"
