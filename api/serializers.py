from rest_framework import serializers
from django.contrib.auth.models import User

from django.contrib.auth.hashers import make_password

from base.models import Category, Item, ItemHistory, Transaction, TransactionItem


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


class PendingOperationSerializer(serializers.Serializer):
    operation = serializers.CharField()
    table_name = serializers.CharField()
    record_id = serializers.IntegerField()
    data = serializers.JSONField()


class DbUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"


class ItemHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemHistory
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class TransactionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionItem
        fields = "__all__"
