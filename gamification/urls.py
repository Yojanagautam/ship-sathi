from django.urls import path
from .views import CheckInView, MyStatsView, LeaderboardView

urlpatterns = [
    path('checkin/', CheckInView.as_view(), name='checkin'),
    path('stats/', MyStatsView.as_view(), name='stats'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]