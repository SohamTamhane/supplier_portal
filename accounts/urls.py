from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('reset_password', views.reset_password1, name='reset_password'),
    path('verify', views.reset_password2, name='verify'),
    path('change_password', views.change_password, name='change_password'),
    path('dashboard', views.dashboard, name='dashboard'),
    
]