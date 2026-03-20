from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import Streak, Badge, LeaderboardEntry


class CheckInView(APIView):
    """User checks in daily to maintain streak"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        today = timezone.now().date()

        streak, created = Streak.objects.get_or_create(user=user)

        if streak.last_study_date == today:
            return Response({"message": "Already checked in today! ✅"})

        # Update streak
        if streak.last_study_date:
            diff = (today - streak.last_study_date).days
            if diff == 1:
                streak.current_streak += 1
            else:
                streak.current_streak = 1
        else:
            streak.current_streak = 1

        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak

        streak.last_study_date = today
        streak.save()

        # Give XP
        user.xp += 50
        user.save()

        # Update leaderboard
        LeaderboardEntry.objects.update_or_create(
            user=user,
            defaults={'xp': user.xp, 'college': user.college}
        )

        # Award badges
        self._check_badges(user, streak)

        return Response({
            "message": "Checked in! 🔥",
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "xp": user.xp,
        })

    def _check_badges(self, user, streak):
        if streak.current_streak >= 7:
            Badge.objects.get_or_create(user=user, badge_type='consistent')
        if streak.current_streak >= 30:
            Badge.objects.get_or_create(user=user, badge_type='streak_master')
        if user.xp >= 1000:
            Badge.objects.get_or_create(user=user, badge_type='legend')


class MyStatsView(APIView):
    """Get current user's XP, streak and badges"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        streak = Streak.objects.filter(user=user).first()
        badges = Badge.objects.filter(user=user).values_list('badge_type', flat=True)

        return Response({
            "xp": user.xp,
            "reliability_score": user.reliability_score,
            "current_streak": streak.current_streak if streak else 0,
            "longest_streak": streak.longest_streak if streak else 0,
            "badges": list(badges),
        })


class LeaderboardView(APIView):
    """Get college leaderboard"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        college = request.user.college
        top = LeaderboardEntry.objects.filter(
            college=college
        ).order_by('-xp')[:10]

        data = [
            {
                "rank": i + 1,
                "username": entry.user.username,
                "xp": entry.xp,
                "college": entry.college,
            }
            for i, entry in enumerate(top)
        ]
        return Response(data)