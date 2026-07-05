from django.urls import path
from . import views

app_name = "services"

urlpatterns = [
    path("", views.home, name="home"),
    path("history/", views.history, name="history"),
    path("register/", views.register_view, name="register"),
    path("login/", views.NagarikLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("favorites/", views.my_favorites, name="my_favorites"),
    path("favorites/toggle/<int:service_id>/", views.toggle_favorite, name="toggle_favorite"),
    path("api/ask/", views.ask_query, name="ask_query"),
]