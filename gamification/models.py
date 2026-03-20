from django.db import models
from django.conf import settings


class Streak(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='streak'
    )
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_study_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.current_streak} days"


class Badge(models.Model):
    BADGE_CHOICES = [
        ('newbie', '🌱 Newbie'),
        ('consistent', '🔥 Consistent Learner'),
        ('streak_master', '⚡ Streak Master'),
        ('top_sharer', '🤝 Top Skill Sharer'),
        ('legend', '👑 Legend'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='badges'
    )
    badge_type = models.CharField(max_length=20, choices=BADGE_CHOICES)
    earned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.badge_type}"


class LeaderboardEntry(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leaderboard'
    )
    college = models.CharField(max_length=150)
    xp = models.IntegerField(default=0)

    class Meta:
        ordering = ['-xp']

    def __str__(self):
        return f"{self.user.email} - XP: {self.xp}"