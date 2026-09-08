from . import views
from django.urls import path

urlpatterns = [
    path('', views.game_list, name='game-list'),
    path('<int:pk>/', views.game_detail, name='game-detail'),

]