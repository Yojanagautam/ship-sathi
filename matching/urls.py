from django.urls import path
from .views import PotentialMatchesView, SwipeView, MyMatchesView

urlpatterns = [
    path('potential/', PotentialMatchesView.as_view(), name='potential-matches'),
    path('swipe/', SwipeView.as_view(), name='swipe'),
    path('my-matches/', MyMatchesView.as_view(), name='my-matches'),
]