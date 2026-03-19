from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Match
from users.models import Profile
from users.serializers import UserSerializer

User = get_user_model()


class PotentialMatchesView(APIView):
    """Get list of users to swipe on"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get users already swiped on
        already_swiped = Match.objects.filter(
            sender=request.user
        ).values_list('receiver_id', flat=True)

        # Get potential matches (same college, not swiped yet)
        potential = User.objects.exclude(
            id=request.user.id
        ).exclude(
            id__in=already_swiped
        ).filter(
            college=request.user.college
        )

        serializer = UserSerializer(potential, many=True)
        return Response(serializer.data)


class SwipeView(APIView):
    """Swipe right or left on a user"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        receiver_id = request.data.get('receiver_id')
        direction = request.data.get('direction')  # 'right' or 'left'

        if not receiver_id or direction not in ['right', 'left']:
            return Response(
                {"error": "Provide receiver_id and direction (right/left)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if direction == 'left':
            Match.objects.create(
                sender=request.user,
                receiver=receiver,
                status='rejected'
            )
            return Response({"message": "Swiped left ❌"})

        # Swipe right
        match, created = Match.objects.get_or_create(
            sender=request.user,
            receiver=receiver,
            defaults={'status': 'pending'}
        )

        # Check if receiver already swiped right on sender
        mutual = Match.objects.filter(
            sender=receiver,
            receiver=request.user,
            status='pending'
        ).first()

        if mutual:
            # It's a match!
            match.status = 'matched'
            match.matched_at = timezone.now()
            match.save()
            mutual.status = 'matched'
            mutual.matched_at = timezone.now()
            mutual.save()
            return Response({"message": "It's a match! 🎉"})

        return Response({"message": "Swiped right ✅ Waiting for them to swipe back!"})


class MyMatchesView(APIView):
    """Get all matched users"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        matches = Match.objects.filter(
            sender=request.user,
            status='matched'
        )
        matched_users = [m.receiver for m in matches]
        serializer = UserSerializer(matched_users, many=True)
        return Response(serializer.data)