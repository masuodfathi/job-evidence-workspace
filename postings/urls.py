from django.urls import path
from .views import posting_list, posting_detail

urlpatterns = [
    # Route the app's base URL to the posting list view.
    path("", posting_list, name="posting_list"),
    # Route the app's detail URL to the posting detail view.
    path("<int:pk>/", posting_detail, name="posting_detail"),
]
