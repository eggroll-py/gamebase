from django.urls import path
from . import views

urlpatterns = [
    path('collection/', views.my_collection, name='my-collection'),

]