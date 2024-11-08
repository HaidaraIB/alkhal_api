from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from django.http import Http404
from api.serializers import UserSerializer
from base.models import User


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
    else:
        error_msg = serializer.errors.get("email")[0]
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
            {"message": "User with the provided ID does not exist"},
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
                "user": serializer.data,
            }
        )
    else:
        return Response(
            {"message": str(serializer.errors)},
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
        return Response(
            {
                "message": "User logged in successfully",
                "user": serializer.data,
            }
        )
    else:
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
