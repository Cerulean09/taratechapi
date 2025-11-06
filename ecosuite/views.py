from django.contrib.auth.hashers import make_password, check_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from supabase import create_client, Client, ClientOptions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
import os
from datetime import datetime, timedelta

def create_supabase_client() -> Client:
    url = os.getenv('TARA_TECH_SUPABASE_CLIENT_URL')
    key = os.getenv('TARA_TECH_SUPABASE_CLIENT_SECRET')
    return create_client(url, key, options=ClientOptions())

def index(request):
    return JsonResponse({"message": "Welcome to Ecosuite API"})

def hello(request):
    return JsonResponse({"message": "Hello from Ecosuite!"})

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    supabase = create_supabase_client()
    try:
        data = request.data.copy()
        data['password'] = make_password(data['password'])
        response = supabase.table('ecosuite_users').insert(data).execute()

        return Response({
            "message": "User registered successfully",
            "data": response.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    supabase = create_supabase_client()
    try:
        email = request.data.get('email')
        password = request.data.get('password')

        # Step 1: Fetch user by email
        response = supabase.table('ecosuite_users').select('*').eq('email', email).execute()
        if not response.data:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

        user = response.data[0]

        # Step 2: Verify password using Django's built-in hasher
        if not check_password(password, user['password']):
            return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Generate JWT tokens with Supabase user data in claims
        # Create a token without Django user - we'll add all user data as claims
        refresh = RefreshToken()
        access = refresh.access_token

        # Add all required user claims for authentication (using camelCase)
        access['id'] = user['id']
        access['email'] = user['email']
        access['fullName'] = user.get('fullName', '')
        access['role'] = user.get('role', 'user')
        access['isActive'] = user.get('isActive', True)
        access['phoneNumber'] = user.get('phoneNumber')
        access['assignedBrandIds'] = user.get('assignedBrandIds', [])
        access['assignedModuleIds'] = user.get('assignedModuleIds', [])
        access['preferences'] = user.get('preferences', {})
        access['dateJoined'] = user.get('dateJoined')
        access['isPendingApproval'] = user.get('isPendingApproval', False)

        # Add same claims to refresh token
        refresh['id'] = user['id']
        refresh['email'] = user['email']

        # Step 5: Return both tokens
        return Response({
            "message": "Login successful",
            "access": str(access),
            "refresh": str(refresh),
            "user": {
                "id": user["id"],
                "email": user["email"],
                "fullName": user.get("fullName", ""),
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    # request.user is now a SupabaseUser object from our custom authentication
    return Response({
        "message": "JWT verified successfully",
        "user": {
            "id": request.user.id,
            "email": request.user.email,
            "fullName": request.user.fullName,
            "role": request.user.role,
            "isActive": request.user.isActive,
            "phoneNumber": request.user.phoneNumber,
            "assignedBrandIds": request.user.assignedBrandIds,
            "assignedModuleIds": request.user.assignedModuleIds,
            "preferences": request.user.preferences,
            "dateJoined": request.user.dateJoined,
            "isPendingApproval": request.user.isPendingApproval,
        }
    })

def logout_user(request):
    supabase = create_supabase_client()
    try:
        supabase.table('ecosuite_users').delete().eq('id', request.data.get('id')).execute()
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)