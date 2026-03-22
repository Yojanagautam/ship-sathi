import requests
from django.shortcuts import render, redirect
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Profile
from .serializers import RegisterSerializer, UserSerializer, ProfileSerializer

User = get_user_model()

BASE_URL = 'http://127.0.0.1:8000/api'


# ─── API Views ───────────────────────────────────────────
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "Welcome to Ship Sathi! 🚀", "user_id": user.id},
            status=status.HTTP_201_CREATED
        )


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


# ─── Template Views ───────────────────────────────────────
def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        response = requests.post(f'{BASE_URL}/auth/login/', json={
            'email': email,
            'password': password
        })

        if response.status_code == 200:
            data = response.json()
            request.session['access_token'] = data['access']
            request.session['refresh_token'] = data['refresh']
            return redirect('/dashboard/')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid email or password'})

    return render(request, 'users/login.html')


def register_page(request):
    if request.method == 'POST':
        data = {
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'password2': request.POST.get('password2'),
            'college': request.POST.get('college'),
        }

        response = requests.post(f'{BASE_URL}/users/register/', json=data)

        if response.status_code == 201:
            return redirect('/login/')
        else:
            error = response.json()
            return render(request, 'users/register.html', {'error': error})

    return render(request, 'users/register.html')


def dashboard_page(request):
    token = request.session.get('access_token')
    if not token:
        return redirect('/login/')

    headers = {'Authorization': f'Bearer {token}'}

    user_res = requests.get(f'{BASE_URL}/users/me/', headers=headers)
    stats_res = requests.get(f'{BASE_URL}/gamification/stats/', headers=headers)
    matches_res = requests.get(f'{BASE_URL}/matching/my-matches/', headers=headers)

    if user_res.status_code == 401:
        return redirect('/login/')

    context = {
        'user': user_res.json(),
        'stats': stats_res.json(),
        'matches': matches_res.json(),
    }
    return render(request, 'users/dashboard.html', context)


def logout_page(request):
    request.session.flush()
    return redirect('/login/')


def checkin_page(request):
    token = request.session.get('access_token')
    if not token:
        return redirect('/login/')

    headers = {'Authorization': f'Bearer {token}'}
    requests.post(f'{BASE_URL}/gamification/checkin/', headers=headers)
    return redirect('/dashboard/')


def matching_page(request):
    token = request.session.get('access_token')
    if not token:
        return redirect('/login/')

    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/matching/potential/', headers=headers)
    users = response.json() if response.status_code == 200 else []

    return render(request, 'matching/matching.html', {'users': users})


def swipe_page(request):
    token = request.session.get('access_token')
    if not token:
        return redirect('/login/')

    if request.method == 'POST':
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'receiver_id': request.POST.get('receiver_id'),
            'direction': request.POST.get('direction'),
        }
        requests.post(f'{BASE_URL}/matching/swipe/', json=data, headers=headers)

    return redirect('/matching/')


def rooms_page(request):
    token = request.session.get('access_token')
    if not token:
        return redirect('/login/')

    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/rooms/my-rooms/', headers=headers)
    rooms = response.json() if response.status_code == 200 else []

    return render(request, 'rooms/rooms.html', {'rooms': rooms})


def create_room_page(request):
    token = request.session.get('access_token')
    if not token:
        return redirect('/login/')

    if request.method == 'POST':
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'name': request.POST.get('name'),
            'is_silent_mode': request.POST.get('is_silent_mode') == 'on',
        }
        requests.post(f'{BASE_URL}/rooms/create/', json=data, headers=headers)

    return redirect('/rooms/')


def join_room_page(request, room_id):
    token = request.session.get('access_token')
    if not token:
        return redirect('/login/')

    headers = {'Authorization': f'Bearer {token}'}
    requests.post(f'{BASE_URL}/rooms/{room_id}/join/', headers=headers)
    return redirect('/rooms/')


def leave_room_page(request, room_id):
    token = request.session.get('access_token')
    if not token:
        return redirect('/login/')

    headers = {'Authorization': f'Bearer {token}'}
    requests.post(f'{BASE_URL}/rooms/{room_id}/leave/', headers=headers)
    return redirect('/rooms/')


def leaderboard_page(request):
    token = request.session.get('access_token')
    if not token:
        return redirect('/login/')

    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/gamification/leaderboard/', headers=headers)
    leaderboard = response.json() if response.status_code == 200 else []

    return render(request, 'gamification/leaderboard.html', {'leaderboard': leaderboard})
def landing_page(request):
    if request.session.get('access_token'):
        return redirect('/dashboard/')
    return render(request, 'landing.html')