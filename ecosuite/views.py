from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password


def index(request):
    return JsonResponse({"message": "Welcome to Ecosuite API"})

def hello(request):
    return JsonResponse({"message": "Hello from Ecosuite!"})

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    email = request.data.get("email")
    password = request.data.get("password")
    full_name = request.data.get("full_name")

    if User.objects.filter(email=email).exists():
        return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create(
        email=email,
        full_name=full_name,
        password=make_password(password),
    )

    refresh = RefreshToken.for_user(user)
    return Response({
        "message": "User registered successfully",
        "token": str(refresh.access_token),
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")

    user = authenticate(request, email=email, password=password)
    if user is None:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

    refresh = RefreshToken.for_user(user)
    return Response({
        "message": "Login successful",
        "token": str(refresh.access_token),
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    return Response({
        "email": user.email,
        "full_name": user.full_name,
    })

def logout_user(request):
    logout(request)
    return Response({"message": "Logout successful"})