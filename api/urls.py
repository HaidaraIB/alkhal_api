from django.urls import path
from .views import update_user_info, add_user, login, get_user

urlpatterns = [
    path("addUser/", add_user, name="add-user"),
    path("updateUserInfo/", update_user_info, name="update-user-info"),
    path("login/", login, name="login"),
    path("getUser/<user_id>/", get_user, name="get-user"),
]
