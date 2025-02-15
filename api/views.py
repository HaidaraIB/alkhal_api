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
    PendingOperationSerializer,
)
from base.models import User, Category, Item, ItemHistory, Transaction, TransactionItem
import sqlite3
import os


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


@api_view(["GET"])
def get_db(_: Request, username: str):
    db_file_content = None
    db_file_name = f"{username}.db"
    if default_storage.exists(db_file_name):
        with default_storage.open(db_file_name, "rb") as f:
            db_file_content = base64.b64encode(f.read()).decode("utf-8")
            original_size = os.path.getsize(default_storage.path(db_file_name))
        return Response(
            {
                "db": db_file_content,
                "size": original_size,
            }
        )
    return Response(
        {
            "message": f"There's no db for the user: {username}",
        },
        status=status.HTTP_404_NOT_FOUND,
    )


@api_view(["POST"])
def upload_db(request: Request):
    serializer = DbUploadSerializer(data=request.data)
    if serializer.is_valid():
        file = serializer.validated_data["file"]

        # Check if the file exists and delete it
        if default_storage.exists(file.name):
            default_storage.delete(file.name)

        # Save the new file
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


@api_view(["POST"])
def sync_pending_operations(request: Request):
    serializer = PendingOperationSerializer(
        data=request.data.get("operations"), many=True
    )
    if serializer.is_valid():
        pending_operations = serializer.validated_data
        username = request.data.get("username")
        db_path = default_storage.path(f"{username}.db")
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                for operation in pending_operations:
                    operation_type = operation["operation"]
                    table_name = operation["table_name"]
                    record_id = operation["record_id"]
                    data = operation["data"]
                    timestamp = operation["timestamp"]
                    uuid = operation["uuid"]

                    # create pending_operations table to insert into if not exists
                    cursor.execute(
                        """
                            CREATE TABLE IF NOT EXISTS pending_operations (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                operation TEXT, -- 'insert', 'update', 'delete'
                                table_name TEXT, -- The table being modified (e.g., 'category', 'item', etc.)
                                record_id INTEGER, -- The ID of the record being modified
                                data TEXT, -- JSON representation of the data
                                timestamp INTEGER, -- Timestamp of the operation
                                uuid TEXT -- Unique id to distinguish users
                            );
                        """
                    )
                    conn.commit()

                    # insert the pending_operation in order to pull it
                    cursor.execute(
                        (
                            "INSERT INTO pending_operations(operation, table_name, record_id, data, timestamp, uuid)"
                            "VALUES (?, ?, ?, ?, ?, ?);"
                        ),
                        [
                            operation_type,
                            table_name,
                            record_id,
                            str(data),
                            timestamp,
                            uuid,
                        ],
                    )

                    trigger_name = f"log_{operation_type}_{table_name}"
                    cursor.execute(
                        f"SELECT sql FROM sqlite_master WHERE type = 'trigger' AND name = '{trigger_name}';"
                    )
                    trigger_definition = cursor.fetchone()
                    
                    cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
                    conn.commit()

                    if operation_type == "insert":
                        columns = ", ".join(data.keys())
                        values = ", ".join([f"'{v}'" for v in data.values()])
                        cursor.execute(
                            f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
                        )

                    elif operation_type == "update":
                        updates = ", ".join([f"{k} = '{v}'" for k, v in data.items()])
                        cursor.execute(
                            f"UPDATE {table_name} SET {updates} WHERE id = {record_id};"
                        )

                    elif operation_type == "delete":
                        cursor.execute(
                            f"DELETE FROM {table_name} WHERE id = {record_id};"
                        )
                    if trigger_definition:
                        cursor.execute(trigger_definition[0])

                conn.commit()

            return Response(
                {
                    "message": "Pending operations synced successfully",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            import traceback
            return Response(
                {
                    "error": traceback.format_exc(),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
def get_pending_operations(
    _: Request,
    username: str,
    last_pending_operation_id: int,
    my_uuid: str,
):
    db_path = default_storage.path(f"{username}.db")
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM pending_operations WHERE id > ? AND uuid != ?",
                [last_pending_operation_id, my_uuid],
            )

            # Fetch column names
            columns = [column[0] for column in cursor.description]

            # Convert tuples to dictionaries
            pending_operations = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response(
            {
                "operations": pending_operations,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class PendingOperationListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = PendingOperationSerializer


class PendingOperationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = PendingOperationSerializer


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
