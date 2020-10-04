from django.urls import path
from . import views

app_name = 'chat'
urlpatterns = [
    path('', views.index, name='index'),
    path('<str:room_name>/', views.room, name='room'),
    path('signin', views.signin, name='signin'),
    path('new_account', views.new_account, name='new_account'),
    path('signout', views.signout, name='signout')
]
