from django.urls import path, include
from . import views

app_name = 'awesome_app'

urlpatterns = [
    path('', views.index, name='main'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),

    path('alert/<str:alert_message>/', views.alert, name='alert'),

    path('create_form/', views.create_post, name='create_form'),
    path('trade/', views.trade, name='trade'),
    path('trade_post/<int:pk>/', views.trade_post,name='trade_post'),
    path('write/', views.write, name='write'),
    path('edit/<int:id>/', views.edit, name='edit'),

    path('search/', views.search, name='search'),
    path('location/', views.location, name='location'),
    path('fix_location/', views.fix_location, name='fix_location'),
    path('set_region/', views.set_region, name='set_region'),
    path('set_region_certification/', views.set_region_certification, name='set_region_certification'),

    path('chat/<int:room_number>/<int:seller_id>', views.current_chat, name='chat'),
    path('chat_msg/<int:room_number>', views.chat_msg, name='chat_msg'),

    path('chat_with_ai/', views.chat_with_ai, name='chat_with_ai'),
]

