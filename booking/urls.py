from django.urls import path
from . import views


urlpatterns = [
    path('request/', views.booking_request, name='booking_request'),
]