from django.urls import path
from .views import CreateRoomView, JoinRoomView, LeaveRoomView, MyRoomsView

urlpatterns = [
    path('create/', CreateRoomView.as_view(), name='create-room'),
    path('my-rooms/', MyRoomsView.as_view(), name='my-rooms'),
    path('<int:room_id>/join/', JoinRoomView.as_view(), name='join-room'),
    path('<int:room_id>/leave/', LeaveRoomView.as_view(), name='leave-room'),
]