# urls py boiler
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),
    path('create_chat', views.create_chat, name='create_chat'),
    path('chat/<str:chat_name>', views.chat, name='chat'),
]
