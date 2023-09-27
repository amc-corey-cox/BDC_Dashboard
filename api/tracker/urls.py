from django.urls import path
from . import views

app_name = "tracker"
urlpatterns = [
    path("", views.TicketsList.as_view(), name="tickets-list"),
    path("profile/", views.UserProfile.as_view(), name="profile"),
    path("<str:pk>/detail/", views.TicketDetail.as_view(), name="ticket-detail"),
    path("user_docs/", views.DocumentationView.as_view(), name="documentation"),
    path("about/", views.AboutView.as_view(), name="about"),
]
