from django.urls import path
from .api_views import UserProfileView, UserProfileStatsView, UserPublicView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/stats/', UserProfileStatsView.as_view(), name='profile-stats'),
    path('users/<str:username>/', UserPublicView.as_view(), name='user-profile')

]