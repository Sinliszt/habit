from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("signup", views.signup, name="signup"),
    path('habit/<int:habit_id>/', views.habit_detail, name='habit_detail'),
    path("create/", views.create_habit, name="create_habit"),
    path('log_shared_habit/', views.log_shared_habit, name='log_shared_habit'),
]