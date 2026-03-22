from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from users.views import (
    landing_page, login_page, register_page, dashboard_page,
    logout_page, checkin_page, matching_page,
    swipe_page, rooms_page, create_room_page,
    join_room_page, leave_room_page, leaderboard_page
)

schema_view = get_schema_view(
    openapi.Info(
        title="Ship Sathi API",
        default_version='v1',
        description="Ship Sathi - Swipe. Match. Study. Grow.",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('api/users/', include('users.urls')),
    path('api/matching/', include('matching.urls')),
    path('api/gamification/', include('gamification.urls')),
    path('api/rooms/', include('rooms.urls')),

    # Template pages
    path('', landing_page, name='home'),       # 👈 landing page
    path('login/', login_page, name='login-page'),
    path('register/', register_page, name='register-page'),
    path('dashboard/', dashboard_page, name='dashboard'),
    path('logout/', logout_page, name='logout'),
    path('checkin/', checkin_page, name='checkin'),
    path('matching/', matching_page, name='matching'),
    path('matching/swipe/', swipe_page, name='swipe'),
    path('rooms/', rooms_page, name='rooms'),
    path('rooms/create/', create_room_page, name='create-room'),
    path('rooms/<int:room_id>/join/', join_room_page, name='join-room'),
    path('rooms/<int:room_id>/leave/', leave_room_page, name='leave-room'),
    path('leaderboard/', leaderboard_page, name='leaderboard'),

    # Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]