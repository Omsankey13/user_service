"""
URL configuration for user_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path
from . import view
 
urlpatterns = [
    path('api/user/create-new-user/', view.create_user, name='create_user'),
    path('api/user/<str:pk>/update-existing-user/', view.update_user, name='update_user'),
    path('api/user/pk=<str:pk>', view.read_user, name='read_user'),
    path('api/user/<str:pk>/delete/', view.delete_user, name='delete_user'),
    path('api/user-service/get-all-user-list', view.get_all_user_list, name='get_all_user_list'),

    #interservice call
    path('api/user-service/get_vehicle_details_in_date_range',view.get_vehicle_details_in_UTC_date_range,name='get_vehicle_details_in_UTC_date_range'),
    path('api/user-service/get_user_details_by_id_with_all_vehicles',view.get_user_details_by_id_with_all_vehicles,name='get_user_details_by_id_with_all_vehicles'),
    path('api/get_vehicle_details_by_date',view.get_vehicles_details_in_date_range,name='get_vehicle_details_by_date')
]