from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import StudyRoom, StudySession


class CreateRoomView(APIView):
    """Create a new study room"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        name = request.data.get('name')
        is_silent = request.data.get('is_silent_mode', False)

        if not name:
            return Response(
                {"error": "Room name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        room = StudyRoom.objects.create(
            name=name,
            created_by=request.user,
            is_silent_mode=is_silent
        )
        room.members.add(request.user)

        return Response({
            "message": "Study room created! 📚",
            "room_id": room.id,
            "name": room.name,
            "is_silent_mode": room.is_silent_mode,
        }, status=status.HTTP_201_CREATED)


class JoinRoomView(APIView):
    """Join an existing study room"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, room_id):
        try:
            room = StudyRoom.objects.get(id=room_id, status='active')
        except StudyRoom.DoesNotExist:
            return Response(
                {"error": "Room not found or closed"},
                status=status.HTTP_404_NOT_FOUND
            )

        room.members.add(request.user)
        StudySession.objects.create(room=room, user=request.user)

        return Response({
            "message": f"Joined {room.name}! 🚀",
            "room_id": room.id,
            "members": room.members.count(),
        })


class LeaveRoomView(APIView):
    """Leave a study room"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, room_id):
        try:
            room = StudyRoom.objects.get(id=room_id)
        except StudyRoom.DoesNotExist:
            return Response(
                {"error": "Room not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        room.members.remove(request.user)

        # Mark session as ended
        session = StudySession.objects.filter(
            room=room,
            user=request.user,
            left_at=None
        ).first()
        if session:
            session.left_at = timezone.now()
            session.save()

        return Response({"message": "Left the room 👋"})


class MyRoomsView(APIView):
    """Get all rooms the user is in"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        rooms = StudyRoom.objects.filter(
            members=request.user,
            status='active'
        )
        data = [
            {
                "id": room.id,
                "name": room.name,
                "members": room.members.count(),
                "is_silent_mode": room.is_silent_mode,
                "created_by": room.created_by.username,
            }
            for room in rooms
        ]
        return Response(data)