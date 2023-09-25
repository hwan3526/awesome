from django.urls import path, include
from . import views

app_name = 'awesome_app'

urlpatterns = [
    path('', views.index, name='main'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),

    path('trade/', views.trade, name='trade'),
    path('trade_post/<int:pk>/', views.trade_post,name='trade_post'),
    path('write/', views.write, name='write'),
    path('edit/<int:id>/', views.edit, name='edit'),

    path('search/', views.search, name='search'),
    path('chat/', views.chat, name='chat'),
    path('location/', views.location, name='location'),
]
