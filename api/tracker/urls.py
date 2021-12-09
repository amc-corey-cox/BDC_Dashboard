from django.urls import path

from . import views

app_name = "tracker"
urlpatterns = [
    # path("/", views.IndexView.as_view(), name="index"),
    path("", views.TicketsList.as_view(), name="tickets-list"),
    path("create/", views.TicketCreate.as_view(), name="ticket-create"),
    path("<int:pk>/update/", views.TicketUpdate.as_view(), name="ticket-update"),
    path("<int:pk>/delete/", views.TicketDelete.as_view(), name="ticket-delete"),
    path("list/", views.TicketsList.as_view(), name="tickets-list"),
    path("<int:pk>/detail/", views.TicketDetail.as_view(), name="ticket-detail"),
    path("user_docs/", views.UserDocsView.as_view(), name="user-docs"),
    path(
        "custodian_instructions/",
        views.CustodianInfoView.as_view(),
        name="user-docs-detail",
    ),
    # 	path('initiate_ticket/', views.initiate_ticket, name='initiate_ticket'),
    # 	path('confirm_initiated_ticket/', views.confirm_initiated_ticket, name='confirm_initiated_ticket'),
    #    path('detail/', views.detail, name='detail'),
    #    path('edit/', views.edit, name='edit'),
    #    path('overview/', views.overview, name='overview')
]
