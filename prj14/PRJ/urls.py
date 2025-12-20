# PRJ/urls.py
from django.contrib import admin
from django.urls import path
from WAPI import views
from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Welcome! Use /Login/ to login."})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Login/', views.Login),
    path('', home),
    # path('Login/', views.login_view, name='login'),
]


