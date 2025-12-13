from django.urls import path
from . import views


urlpatterns = [
    path('request/', views.booking_request, name='booking_request'),
    path('slots/<str:date_str>/', views.get_slots_for_date, name='get_slots'),
]