import base64
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from django.http import Http404
from api.serializers import (
    UserSerializer,
    DbUploadSerializer,
    CategorySerializer,
    ItemHistorySerializer,
    ItemSerializer,
    TransactionItemSerializer,
    TransactionSerializer,
)
from base.models import User, Category, Item, ItemHistory, Transaction, TransactionItem


@api_view(["POST"])
def add_user(request: Request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "User added successfully",
                "me": serializer.data,
            }
        )
    error_msg = serializer.errors.get("username")[0]
    return Response(
        {
            "message": error_msg,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["POST"])
def update_user_info(request: Request):
    try:
        user = get_object_or_404(User, id=request.data.get("id"))
    except Http404:
        return Response(
            {
                "message": "User with the provided ID does not exist",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = UserSerializer(data=request.data, instance=user)

    if serializer.is_valid():
        # .save() here will call .update(),
        # because we're passing the User object as an instance to UserSerializer.
        serializer.save()
        return Response(
            {
                "message": "User updated successfully",
                "me": serializer.data,
            }
        )
    return Response(
        {
            "message": str(serializer.errors),
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["POST"])
def login(request: Request):
    try:
        user = get_object_or_404(User, username=request.data["username"])
    except Http404:
        return Response(
            {
                "message": "Username not found",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    is_password_correct = check_password(request.data["password"], user.password)

    if is_password_correct:
        serializer = UserSerializer(user)
        db_file_content = None
        db_file_name = f"{user.username}.db"
        if default_storage.exists(db_file_name):
            with default_storage.open(db_file_name, "rb") as f:
                db_file_content = base64.b64encode(f.read()).decode("utf-8")

        response_data = {
            "message": "User logged in successfully",
            "me": serializer.data,
        }

        if db_file_content:
            response_data["db"] = db_file_content

        return Response(response_data)
    return Response(
        {
            "message": "Icorrect password",
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
def get_user(_: Request, user_id: int):
    user = User.objects.filter(id=user_id)[0]
    if not user:
        return Response(
            {
                "message": f"There's no user with an id: {user_id}",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer: UserSerializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(["POST"])
def upload_db(request: Request):
    serializer = DbUploadSerializer(data=request.data)
    if serializer.is_valid():
        file = serializer.validated_data["file"]
        file_name = default_storage.save(file.name, ContentFile(file.read()))
        file_url = default_storage.url(file_name)

        # Add any additional processing here, like validating the SQLite file

        return Response(
            {
                "file_url": file_url,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ItemListCreateView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class ItemHistoryListCreateView(generics.ListCreateAPIView):
    queryset = ItemHistory.objects.all()
    serializer_class = ItemHistorySerializer


class ItemHistoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ItemHistory.objects.all()
    serializer_class = ItemHistorySerializer


class TransactionListCreateView(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionItemListCreateView(generics.ListCreateAPIView):
    queryset = TransactionItem.objects.all()
    serializer_class = TransactionItemSerializer


class TransactionItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TransactionItem.objects.all()
    serializer_class = TransactionItemSerializer
