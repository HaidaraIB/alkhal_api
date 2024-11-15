from django.urls import path
from .views import (
    update_user_info,
    add_user,
    login,
    get_user,
    upload_db,
    CategoryListCreateView,
    ItemDetailView,
    CategoryDetailView,
    ItemListCreateView,
    ItemHistoryDetailView,
    TransactionDetailView,
    ItemHistoryListCreateView,
    TransactionItemDetailView,
    TransactionListCreateView,
    TransactionItemListCreateView,
)

urlpatterns = [
    path("addUser/", add_user, name="add-user"),
    path("updateUserInfo/", update_user_info, name="update-user-info"),
    path("login/", login, name="login"),
    path("getUser/<user_id>/", get_user, name="get-user"),
    path("uploadDb/", upload_db, name="upload-db"),
    #######################################
    path(
        "categories/",
        CategoryListCreateView.as_view(),
        name="category-list-create",
    ),
    path(
        "categories/<int:pk>/",
        CategoryDetailView.as_view(),
        name="category-detail",
    ),
    path(
        "items/",
        ItemListCreateView.as_view(),
        name="item-list-create",
    ),
    path(
        "items/<int:pk>/",
        ItemDetailView.as_view(),
        name="item-detail",
    ),
    path(
        "item-history/",
        ItemHistoryListCreateView.as_view(),
        name="item-history-list-create",
    ),
    path(
        "item-history/<int:pk>/",
        ItemHistoryDetailView.as_view(),
        name="item-history-detail",
    ),
    path(
        "transactions/",
        TransactionListCreateView.as_view(),
        name="transaction-list-create",
    ),
    path(
        "transactions/<int:pk>/",
        TransactionDetailView.as_view(),
        name="transaction-detail",
    ),
    path(
        "transaction-items/",
        TransactionItemListCreateView.as_view(),
        name="transaction-item-list-create",
    ),
    path(
        "transaction-items/<int:pk>/",
        TransactionItemDetailView.as_view(),
        name="transaction-item-detail",
    ),
]
