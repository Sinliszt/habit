from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("signup", views.signup, name="signup"),
    path("habit/<int:habit_id>/", views.habit_detail, name="habit_detail"),
    path("create/", views.create_habit, name="create_habit"),
    path("log_shared_habit/", views.log_shared_habit, name="log_shared_habit"),
    path("friends/", views.friends_list, name="friends_list"),
    path("friend-request/send/<int:user_id>/", views.send_friend_request, name="send_friend_request"),
    path("friend-request/accept/<int:request_id>/", views.accept_friend_request, name="accept_friend_request"),
    path("search-users/", views.search_users, name="search_users"),
    path("send-request/<int:user_id>/", views.send_friend_request, name="send_friend_request"),
    path("profile/<str:username>/", views.profile_view, name="profile_view"),
    path("shared/", views.shared_habits_view, name="shared_habits"),
]