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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_users(request):
    """Get all users"""
    supabase = create_supabase_client()
    try:
        response = supabase.table('ecosuite_users').select('*').execute()
        users = response.data if response.data else []
        
        # Remove password field from each user for security
        for user in users:
            if 'password' in user:
                del user['password']
        
        return Response({
            "users": users
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    """Update an existing user"""
    supabase = create_supabase_client()
    try:
        data = request.data.copy()
        
        # Hash password if provided
        if 'password' in data and data['password']:
            data['password'] = make_password(data['password'])
        
        # Update timestamp if field exists
        if 'updatedAt' in data or 'dateJoined' in data:
            data['updatedAt'] = datetime.utcnow().isoformat()
        
        # Update user
        response = supabase.table('ecosuite_users').update(data).eq('id', user_id).execute()
        
        if response.data:
            # Remove password from response for security
            user_data = response.data[0].copy()
            if 'password' in user_data:
                del user_data['password']
            
            return Response({
                "message": "User updated successfully",
                "user": user_data
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User not found or update failed"}, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ======================================================
# Brand Management Views
# ======================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_brands(request):
    """Get all brands"""
    supabase = create_supabase_client()
    try:
        response = supabase.table('ecosuite_brands').select('*').execute()
        brands = response.data if response.data else []
        
        return Response({
            "brands": brands
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_brand(request, brand_id):
    """Get a single brand by ID"""
    supabase = create_supabase_client()
    try:
        response = supabase.table('ecosuite_brands').select('*').eq('id', brand_id).execute()
        
        if response.data and len(response.data) > 0:
            return Response({
                "brand": response.data[0]
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Brand not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_brand(request):
    """Create a new brand"""
    supabase = create_supabase_client()
    try:
        data = request.data.copy()
        
        # Ensure required fields
        if not data.get('name'):
            return Response({"error": "Brand name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Set timestamps if not provided
        now = datetime.utcnow().isoformat()
        if 'createdAt' not in data:
            data['createdAt'] = now
        if 'updatedAt' not in data:
            data['updatedAt'] = now
        
        # Set createdBy/updatedBy from authenticated user if not provided
        if 'createdBy' not in data:
            data['createdBy'] = request.user.id
        if 'updatedBy' not in data:
            data['updatedBy'] = request.user.id
        
        # Ensure default values
        if 'status' not in data:
            data['status'] = 'active'
        if 'outletIds' not in data:
            data['outletIds'] = []
        if 'userIds' not in data:
            data['userIds'] = []
        if 'moduleAccess' not in data:
            data['moduleAccess'] = {}
        
        # Insert brand
        response = supabase.table('ecosuite_brands').insert(data).execute()
        
        if response.data:
            return Response({
                "message": "Brand created successfully",
                "brand": response.data[0]
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Failed to create brand"}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_brand(request, brand_id):
    """Update an existing brand"""
    supabase = create_supabase_client()
    try:
        data = request.data.copy()
        
        # Update timestamp
        data['updatedAt'] = datetime.utcnow().isoformat()
        
        # Set updatedBy from authenticated user if not provided
        if 'updatedBy' not in data:
            data['updatedBy'] = request.user.id
        
        # Update brand
        response = supabase.table('ecosuite_brands').update(data).eq('id', brand_id).execute()
        
        if response.data:
            return Response({
                "message": "Brand updated successfully",
                "brand": response.data[0]
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Brand not found or update failed"}, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_brand(request, brand_id):
    """Delete a brand"""
    supabase = create_supabase_client()
    try:
        response = supabase.table('ecosuite_brands').delete().eq('id', brand_id).execute()
        
        if response.data:
            return Response({
                "message": "Brand deleted successfully"
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Brand not found"}, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)