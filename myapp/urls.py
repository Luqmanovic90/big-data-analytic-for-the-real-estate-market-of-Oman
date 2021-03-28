from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('data', views.data, name='data'),
    path('user', views.user, name='user'),
    path('edituser', views.edituser, name='edituser'),
    path('scraping', views.scraping, name='scraping'),
]