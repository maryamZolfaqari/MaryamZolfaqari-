from django.contrib import admin
from django.urls import path
import WAPI.views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('Login/', WAPI.views.Login),
]
