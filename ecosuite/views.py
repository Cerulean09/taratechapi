from django.contrib.auth.hashers import make_password, check_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from supabase import create_client, Client, ClientOptions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
import os
import uuid
import json
import re
from datetime import datetime, timedelta
from django.utils import timezone
import requests

def resolve_request_environment(request):
    if hasattr(request, 'query_params'):
        env = request.query_params.get('environment')
        if env:
            return env
    try:
        data_env = request.data.get('environment')
        if data_env:
            return data_env
    except AttributeError:
        pass
    return None



def extract_receipt_id(reservation):
    return (
        reservation.get('receiptId')
        or reservation.get('receiptID')
        or reservation.get('clientReferenceId')
        or reservation.get('invoiceNo')
        or reservation.get('id')
    )


def sync_crm_customer_from_reservation(supabase, reservation_record, request_user_id):
    if not reservation_record:
        return

    customer_phone = reservation_record.get('customerPhone')
    if not customer_phone:
        return

    receipt_id = extract_receipt_id(reservation_record)
    brand_id = reservation_record.get('brandId')
    outlet_id = reservation_record.get('outletId')
    customer_name = reservation_record.get('customerName') or ''
    notes = reservation_record.get('notes')
    utc_offset = reservation_record.get('utcOffset')

    if not brand_id or not outlet_id:
        return

    now = timezone.now().isoformat()

    existing_response = supabase.table('ecosuite_crm_customers').select('*').eq('phone', customer_phone).execute()
    existing_customers = existing_response.data or []

    if existing_customers:
        crm_customer = existing_customers[0]
        existing_receipts = crm_customer.get('receiptIds') or []

        if isinstance(existing_receipts, str):
            try:
                existing_receipts = json.loads(existing_receipts)
            except (ValueError, TypeError):
                existing_receipts = [existing_receipts]

        if not isinstance(existing_receipts, list):
            existing_receipts = [existing_receipts]

        if receipt_id and receipt_id in existing_receipts:
            return

        updated_receipts = existing_receipts.copy()
        if receipt_id:
            updated_receipts.append(receipt_id)

        update_payload = {
            'updatedAt': now,
            'updatedBy': request_user_id,
            'receiptIds': updated_receipts,
        }

        supabase.table('ecosuite_crm_customers').update(update_payload).eq('id', crm_customer['id']).execute()
    else:
        new_customer = {
            'id': str(uuid.uuid4()),
            'brandId': brand_id,
            'outletId': outlet_id,
            'fullName': customer_name,
            'phone': customer_phone,
            'email': reservation_record.get('customerEmail'),
            'receiptIds': [receipt_id] if receipt_id else [],
            'notes': notes,
            'createdAt': now,
            'updatedAt': now,
            'createdBy': request_user_id,
            'updatedBy': request_user_id,
            'utcOffset': utc_offset,
        }

        supabase.table('ecosuite_crm_customers').insert(new_customer).execute()


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
            data['updatedAt'] = timezone.now().isoformat()
        
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
@permission_classes([AllowAny])
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
        now = timezone.now().isoformat()
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
        if 'outlets' not in data:
            data['outlets'] = []
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
        data['updatedAt'] = timezone.now().isoformat()
        
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

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def suspend_brand(request, brand_id):
    """Suspend a brand (set status to 'suspended' instead of deleting)"""
    supabase = create_supabase_client()
    try:
        data = {
            'status': 'suspended',
            'updatedAt': timezone.now().isoformat(),
            'updatedBy': request.user.id
        }
        
        response = supabase.table('ecosuite_brands').update(data).eq('id', brand_id).execute()
        
        if response.data:
            return Response({
                "message": "Brand suspended successfully",
                "brand": response.data[0]
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Brand not found"}, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def upsert_brand(request):
    """Add or update a brand. If id is provided, updates existing brand; otherwise creates new one."""
    supabase = create_supabase_client()
    try:
        data = request.data.copy()
        
        # Ensure required fields
        if not data.get('name'):
            return Response({"error": "Brand name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        brand_id = data.get('id')
        now = timezone.now().isoformat()
        
        if brand_id:
            # Update existing brand
            # Remove id from data for update
            update_data = {k: v for k, v in data.items() if k != 'id'}
            update_data['updatedAt'] = now
            
            # Set updatedBy from authenticated user if not provided
            if 'updatedBy' not in update_data:
                update_data['updatedBy'] = request.user.id
            
            # Ensure status is valid (don't allow deletion, only suspend)
            if 'status' in update_data and update_data['status'] == 'deleted':
                update_data['status'] = 'suspended'
            
            response = supabase.table('ecosuite_brands').update(update_data).eq('id', brand_id).execute()
            
            if response.data:
                return Response({
                    "message": "Brand updated successfully",
                    "brand": response.data[0]
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Brand not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Create new brand
            # Generate new ID if not provided
            if 'id' not in data:
                return Response({"error": "Brand ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Set timestamps
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
            if 'outlets' not in data:
                data['outlets'] = []
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_brand_logo(request, brand_id):
    """Upload a brand logo to Supabase Storage"""
    supabase = create_supabase_client()
    try:
        # Check if file is provided
        if 'logo' not in request.FILES:
            return Response({"error": "Logo file is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        logo_file = request.FILES['logo']
        
        # Validate file type (optional - you can add more validation)
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        file_extension = os.path.splitext(logo_file.name)[1].lower()
        if file_extension not in allowed_extensions:
            return Response({
                "error": f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_name = f"{file_id}{file_extension}"
        storage_path = f"logos/{file_name}"
        
        # Read file content as bytes
        file_content = logo_file.read()
        
        # Upload to Supabase Storage
        # Note: The bucket name should match your Supabase storage bucket
        storage_response = supabase.storage.from_('ecosuite-brand-documents').upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": logo_file.content_type}
        )
        
        # Get public URL - construct it from Supabase URL
        supabase_url = os.getenv('TARA_TECH_SUPABASE_CLIENT_URL')
        # Remove trailing slash if present
        supabase_url = supabase_url.rstrip('/')
        logo_url = f"{supabase_url}/storage/v1/object/public/ecosuite-brand-documents/{storage_path}"
        
        # Update brand with logo URL
        update_data = {
            'logoUrl': logo_url,
            'updatedAt': timezone.now().isoformat(),
            'updatedBy': request.user.id
        }
        
        brand_response = supabase.table('ecosuite_brands').update(update_data).eq('id', brand_id).execute()
        
        if brand_response.data:
            return Response({
                "message": "Logo uploaded successfully",
                "logoUrl": logo_url,
                "brand": brand_response.data[0]
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Brand not found"}, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_brand_floor_image(request, brand_id):
    """Upload a brand floor plan image to Supabase Storage"""
    supabase = create_supabase_client()
    try:
        # Check if file is provided
        if 'floorImage' not in request.FILES:
            return Response({"error": "Floor image file is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        floor_image_file = request.FILES['floorImage']
        
        # Validate file type (optional - you can add more validation)
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        file_extension = os.path.splitext(floor_image_file.name)[1].lower()
        if file_extension not in allowed_extensions:
            return Response({
                "error": f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_name = f"{file_id}{file_extension}"
        storage_path = f"floor-plans/{file_name}"
        
        # Read file content as bytes
        file_content = floor_image_file.read()
        
        # Upload to Supabase Storage
        # Note: The bucket name should match your Supabase storage bucket
        storage_response = supabase.storage.from_('ecosuite-brand-documents').upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": floor_image_file.content_type}
        )
        
        # Get public URL - construct it from Supabase URL
        supabase_url = os.getenv('TARA_TECH_SUPABASE_CLIENT_URL')
        # Remove trailing slash if present
        supabase_url = supabase_url.rstrip('/')
        floor_image_url = f"{supabase_url}/storage/v1/object/public/ecosuite-brand-documents/{storage_path}"
        
        # Update brand with floor image URL
        update_data = {
            'floorImageUrl': floor_image_url,
            'updatedAt': timezone.now().isoformat(),
            'updatedBy': request.user.id
        }
        
        brand_response = supabase.table('ecosuite_brands').update(update_data).eq('id', brand_id).execute()
        
        if brand_response.data:
            return Response({
                "message": "Floor image uploaded successfully",
                "floorImageUrl": floor_image_url,
                "brand": brand_response.data[0]
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Brand not found"}, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_outlet_floor_image(request, outlet_id):
    """Upload an outlet floor plan image to Supabase Storage"""
    supabase = create_supabase_client()
    try:
        # Check if file is provided
        if 'floorImage' not in request.FILES:
            return Response({"error": "Floor image file is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if floorNumber is provided
        floor_number = request.data.get('floorNumber')
        if not floor_number:
            return Response({"error": "Floor number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Convert floor number to string (keys in JSON should be strings)
        floor_number = str(floor_number)
        
        floor_image_file = request.FILES['floorImage']
        
        # Validate file type (optional - you can add more validation)
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        file_extension = os.path.splitext(floor_image_file.name)[1].lower()
        if file_extension not in allowed_extensions:
            return Response({
                "error": f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_name = f"{file_id}{file_extension}"
        storage_path = f"outlet-floor-plans/{file_name}"
        
        # Read file content as bytes
        file_content = floor_image_file.read()
        
        # Upload to Supabase Storage
        # Note: The bucket name should match your Supabase storage bucket
        storage_response = supabase.storage.from_('ecosuite-brand-documents').upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": floor_image_file.content_type}
        )
        
        # Get public URL - construct it from Supabase URL
        supabase_url = os.getenv('TARA_TECH_SUPABASE_CLIENT_URL')
        # Remove trailing slash if present
        supabase_url = supabase_url.rstrip('/')
        floor_image_url = f"{supabase_url}/storage/v1/object/public/ecosuite-brand-documents/{storage_path}"
        
        # Find the brand that contains this outlet
        brands_response = supabase.table('ecosuite_brands').select('*').execute()
        
        if not brands_response.data:
            return Response({"error": "No brands found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Search through all brands to find the one containing this outlet
        brand_found = None
        outlet_found = None
        outlet_index = -1
        
        for brand in brands_response.data:
            outlets = brand.get('outlets', [])
            if isinstance(outlets, list):
                for idx, outlet in enumerate(outlets):
                    if isinstance(outlet, dict) and outlet.get('id') == outlet_id:
                        brand_found = brand
                        outlet_found = outlet
                        outlet_index = idx
                        break
                if brand_found:
                    break
        
        if not brand_found or not outlet_found:
            return Response({"error": "Outlet not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get or initialize floorLayoutImages
        floor_layout_images = outlet_found.get('floorLayoutImages', {})
        if not isinstance(floor_layout_images, dict):
            floor_layout_images = {}
        
        # Update the floorLayoutImages with the new image URL for this floor number
        floor_layout_images[floor_number] = floor_image_url
        
        # Update the outlet's floorLayoutImages
        outlet_found['floorLayoutImages'] = floor_layout_images
        
        # Update the outlets array in the brand
        outlets = brand_found.get('outlets', [])
        outlets[outlet_index] = outlet_found
        
        # Update the brand with the modified outlets array
        update_data = {
            'outlets': outlets,
            'updatedAt': timezone.now().isoformat(),
            'updatedBy': request.user.id
        }
        
        brand_response = supabase.table('ecosuite_brands').update(update_data).eq('id', brand_found['id']).execute()
        
        if brand_response.data:
            return Response({
                "message": "Outlet floor image uploaded successfully",
                "floorNumber": floor_number,
                "floorImageUrl": floor_image_url,
                "floorLayoutImages": floor_layout_images,
                "outlet": outlet_found,
                "brand": brand_response.data[0]
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to update brand"}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def upsert_table(request, table_id):
    """Insert or update a table. If table exists, updates it; otherwise creates a new one."""
    supabase = create_supabase_client()
    try:
        data = request.data.copy()
        
        # Find the brand that contains the outlet that contains this table
        brands_response = supabase.table('ecosuite_brands').select('*').execute()
        
        if not brands_response.data:
            return Response({"error": "No brands found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Search through all brands to find the one containing this table
        brand_found = None
        outlet_found = None
        outlet_index = -1
        table_found = None
        floor_number = None
        table_index = -1
        is_new_table = False
        
        for brand in brands_response.data:
            outlets = brand.get('outlets', [])
            if isinstance(outlets, list):
                for outlet_idx, outlet in enumerate(outlets):
                    if isinstance(outlet, dict):
                        tables_map = outlet.get('tables', {})
                        if isinstance(tables_map, dict):
                            # Search through all floors in the tables map
                            for floor_num_str, tables_list in tables_map.items():
                                if isinstance(tables_list, list):
                                    for table_idx, table in enumerate(tables_list):
                                        if isinstance(table, dict) and table.get('id') == table_id:
                                            brand_found = brand
                                            outlet_found = outlet
                                            outlet_index = outlet_idx
                                            table_found = table
                                            floor_number = floor_num_str
                                            table_index = table_idx
                                            break
                                    if table_found:
                                        break
                        if table_found:
                            break
                if table_found:
                    break
        
        # If table not found, we need to create it
        if not table_found:
            is_new_table = True
            
            # For new table, we need outletId and floorNumber from request
            outlet_id = data.get('outletId')
            floor_number = str(data.get('floorNumber', '1'))  # Default to floor 1 if not provided
            
            if not outlet_id:
                return Response({"error": "outletId is required for new tables"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Find the outlet
            for brand in brands_response.data:
                outlets = brand.get('outlets', [])
                if isinstance(outlets, list):
                    for outlet_idx, outlet in enumerate(outlets):
                        if isinstance(outlet, dict) and outlet.get('id') == outlet_id:
                            brand_found = brand
                            outlet_found = outlet
                            outlet_index = outlet_idx
                            break
                    if outlet_found:
                        break
            
            if not brand_found or not outlet_found:
                return Response({"error": "Outlet not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Create new table
            now = timezone.now().isoformat()
            table_found = {
                'id': table_id,
                'brandId': outlet_found.get('brandId', brand_found.get('id')),
                'outletId': outlet_id,
                'name': data.get('name', ''),
                'capacity': data.get('capacity', 0),
                'status': data.get('status', 'available'),
                'currentReservationId': data.get('currentReservationId'),
                'layoutPosition': data.get('layoutPosition'),
                'createdAt': data.get('createdAt', now),
                'updatedAt': now,
                'createdBy': request.user.id,
                'updatedBy': request.user.id
            }
        
        # Update the table with new data (for both new and existing tables)
        table_found.update({
            'name': data.get('name', table_found.get('name', '')),
            'capacity': data.get('capacity', table_found.get('capacity', 0)),
            'status': data.get('status', table_found.get('status', 'available')),
            'currentReservationId': data.get('currentReservationId', table_found.get('currentReservationId')),
            'layoutPosition': data.get('layoutPosition', table_found.get('layoutPosition')),
            'updatedAt': timezone.now().isoformat(),
            'updatedBy': request.user.id
        })
        
        # Ensure required fields are present
        if 'id' not in table_found:
            table_found['id'] = table_id
        if 'brandId' not in table_found:
            table_found['brandId'] = outlet_found.get('brandId', brand_found.get('id'))
        if 'outletId' not in table_found:
            table_found['outletId'] = outlet_found.get('id')
        if 'createdAt' not in table_found:
            table_found['createdAt'] = timezone.now().isoformat()
        if 'createdBy' not in table_found:
            table_found['createdBy'] = request.user.id
        
        # Get or initialize tables map
        tables_map = outlet_found.get('tables', {})
        if not isinstance(tables_map, dict):
            tables_map = {}
        
        # Check if floor number is being changed (for updates)
        new_floor_number = str(data.get('floorNumber', floor_number)) if not is_new_table else floor_number
        
        # If updating and floor number changed, remove from old floor
        if not is_new_table and new_floor_number != floor_number:
            # Remove table from old floor
            if floor_number in tables_map and isinstance(tables_map[floor_number], list):
                tables_map[floor_number] = [t for t in tables_map[floor_number] if not (isinstance(t, dict) and t.get('id') == table_id)]
            floor_number = new_floor_number
        
        # Ensure the floor number exists in the tables map
        if floor_number not in tables_map:
            tables_map[floor_number] = []
        
        # Update or insert the table in the list
        if is_new_table:
            # Add new table to the list
            tables_map[floor_number].append(table_found)
        else:
            # Update existing table
            # First, try to find and update in the current floor
            found = False
            if isinstance(tables_map[floor_number], list):
                for idx, table in enumerate(tables_map[floor_number]):
                    if isinstance(table, dict) and table.get('id') == table_id:
                        tables_map[floor_number][idx] = table_found
                        found = True
                        break
            
            # If not found in current floor, append it (shouldn't happen, but handle it)
            if not found:
                tables_map[floor_number].append(table_found)
        
        # Update the outlet's tables map
        outlet_found['tables'] = tables_map
        
        # Update the outlets array in the brand
        outlets = brand_found.get('outlets', [])
        outlets[outlet_index] = outlet_found
        
        # Update the brand with the modified outlets array
        update_data = {
            'outlets': outlets,
            'updatedAt': timezone.now().isoformat(),
            'updatedBy': request.user.id
        }
        
        brand_response = supabase.table('ecosuite_brands').update(update_data).eq('id', brand_found['id']).execute()
        
        if brand_response.data:
            message = "Table created successfully" if is_new_table else "Table updated successfully"
            status_code = status.HTTP_201_CREATED if is_new_table else status.HTTP_200_OK
            return Response({
                "message": message,
                "table": table_found,
                "outlet": outlet_found,
                "brand": brand_response.data[0]
            }, status=status_code)
        else:
            return Response({"error": "Failed to update brand"}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'PUT', 'PATCH'])
@permission_classes([AllowAny])
def upsert_reservation(request, reservation_id):
    """Insert or update a reservation. If reservation exists, updates it; otherwise creates a new one."""
    supabase = create_supabase_client()
    try:
        data = request.data.copy()
        
        # Check if reservation exists
        existing_response = supabase.table('ecosuite_reservations').select('*').eq('id', reservation_id).execute()
        is_new_reservation = not existing_response.data or len(existing_response.data) == 0
        
        now = timezone.now().isoformat()
        
        if is_new_reservation:
            # Create new reservation
            # Ensure required fields
            if not data.get('brandId'):
                return Response({"error": "brandId is required"}, status=status.HTTP_400_BAD_REQUEST)
            if not data.get('outletId'):
                return Response({"error": "outletId is required"}, status=status.HTTP_400_BAD_REQUEST)
            if not data.get('customerName'):
                return Response({"error": "customerName is required"}, status=status.HTTP_400_BAD_REQUEST)
            if not data.get('customerPhone'):
                return Response({"error": "customerPhone is required"}, status=status.HTTP_400_BAD_REQUEST)
            if not data.get('numberOfGuests'):
                return Response({"error": "numberOfGuests is required"}, status=status.HTTP_400_BAD_REQUEST)
            if not data.get('reservationDateTime'):
                return Response({"error": "reservationDateTime is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            reservation_data = {
                'id': reservation_id,
                'brandId': data.get('brandId'),
                'outletId': data.get('outletId'),
                'customerName': data.get('customerName'),
                'customerPhone': data.get('customerPhone'),
                'numberOfGuests': data.get('numberOfGuests'),
                'reservationDateTime': data.get('reservationDateTime'),
                'status': data.get('status', 'pending'),
                'tableId': data.get('tableId'),
                'notes': data.get('notes'),
                'utcOffset': data.get('utcOffset'),
                'createdAt': data.get('createdAt', now),
                'updatedAt': now,
                'createdBy': request.user.id,
                'updatedBy': request.user.id,
                'payments': data.get('payments', []),
                'checkedInAt': data.get('checkedInAt', None),
                'checkedInBy': data.get('checkedInBy', None),
                'checkedOutAt': data.get('checkedOutAt', None),
                'checkedOutBy': data.get('checkedOutBy', None),
            }
            
            # Insert reservation
            response = supabase.table('ecosuite_reservations').insert(reservation_data).execute()
            
            if response.data:
                reservation_record = response.data[0]
                try:
                    sync_crm_customer_from_reservation(supabase, reservation_record, request.user.id)
                except Exception as crm_error:
                    print(f"CRM sync error (create): {crm_error}")
                return Response({
                    "message": "Reservation created successfully",
                    "reservation": response.data[0]
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Failed to create reservation"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Update existing reservation
            existing_reservation = existing_response.data[0]
            
            # Update fields, preserving existing values if not provided
            # Use 'in' check to allow None values to be set explicitly
            update_data = {
                'updatedAt': now,
                'updatedBy': request.user.id
            }
            
            # Only update fields that are provided in the request
            if 'brandId' in data:
                update_data['brandId'] = data.get('brandId')
            if 'outletId' in data:
                update_data['outletId'] = data.get('outletId')
            if 'customerName' in data:
                update_data['customerName'] = data.get('customerName')
            if 'customerPhone' in data:
                update_data['customerPhone'] = data.get('customerPhone')
            if 'numberOfGuests' in data:
                update_data['numberOfGuests'] = data.get('numberOfGuests')
            if 'reservationDateTime' in data:
                update_data['reservationDateTime'] = data.get('reservationDateTime')
            if 'status' in data:
                update_data['status'] = data.get('status')
            if 'tableId' in data:
                update_data['tableId'] = data.get('tableId')
            if 'notes' in data:
                update_data['notes'] = data.get('notes')
            if 'utcOffset' in data:
                update_data['utcOffset'] = data.get('utcOffset')
            if 'payments' in data:
                update_data['payments'] = data.get('payments')
            if 'checkedInAt' in data:
                update_data['checkedInAt'] = data.get('checkedInAt')
            if 'checkedInBy' in data:
                update_data['checkedInBy'] = data.get('checkedInBy')
            if 'checkedOutAt' in data:
                update_data['checkedOutAt'] = data.get('checkedOutAt')
            if 'checkedOutBy' in data:
                update_data['checkedOutBy'] = data.get('checkedOutBy')
            
            # Update reservation
            response = supabase.table('ecosuite_reservations').update(update_data).eq('id', reservation_id).execute()
            
            if response.data:
                reservation_record = response.data[0] if response.data else {**existing_reservation, **update_data}
                try:
                    sync_crm_customer_from_reservation(supabase, reservation_record, request.user.id)
                except Exception as crm_error:
                    print(f"CRM sync error (update): {crm_error}")
                return Response({
                    "message": "Reservation updated successfully",
                    "reservation": response.data[0]
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to update reservation"}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def upsert_crm_customer(request, customer_id):
    """Insert or update a CRM customer in ecosuite_crm_customers."""
    supabase = create_supabase_client()
    try:
        data = request.data.copy()

        receipt_ids = data.get('receiptIds')
        if receipt_ids is None:
            receipt_ids = []
        elif isinstance(receipt_ids, str):
            try:
                receipt_ids = json.loads(receipt_ids)
            except (ValueError, TypeError):
                receipt_ids = [receipt_ids]
        elif not isinstance(receipt_ids, list):
            receipt_ids = [receipt_ids]

        now = timezone.now().isoformat()

        existing_response = supabase.table('ecosuite_crm_customers').select('*').eq('id', customer_id).execute()
        is_new_customer = not existing_response.data or len(existing_response.data) == 0

        if is_new_customer:
            required_fields = ['brandId', 'outletId', 'fullName']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return Response({
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }, status=status.HTTP_400_BAD_REQUEST)

            customer_data = {
                'id': customer_id,
                'brandId': data.get('brandId'),
                'outletId': data.get('outletId'),
                'fullName': data.get('fullName'),
                'phone': data.get('phone'),
                'email': data.get('email'),
                'receiptIds': receipt_ids,
                'notes': data.get('notes'),
                'createdAt': data.get('createdAt', now),
                'updatedAt': now,
                'createdBy': data.get('createdBy', request.user.id),
                'updatedBy': data.get('updatedBy', request.user.id),
                'utcOffset': data.get('utcOffset'),
            }

            response = supabase.table('ecosuite_crm_customers').insert(customer_data).execute()

            if response.data:
                return Response({
                    "message": "CRM customer created successfully",
                    "customer": response.data[0]
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Failed to create CRM customer"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            existing_customer = existing_response.data[0]
            update_data = {
                'updatedAt': now,
                'updatedBy': request.user.id
            }

            if 'brandId' in data:
                update_data['brandId'] = data.get('brandId')
            if 'outletId' in data:
                update_data['outletId'] = data.get('outletId')
            if 'fullName' in data:
                update_data['fullName'] = data.get('fullName')
            if 'phone' in data:
                update_data['phone'] = data.get('phone')
            if 'email' in data:
                update_data['email'] = data.get('email')
            if 'notes' in data:
                update_data['notes'] = data.get('notes')
            if 'receiptIds' in data or receipt_ids != existing_customer.get('receiptIds', []):
                update_data['receiptIds'] = receipt_ids
            if 'createdAt' in data:
                update_data['createdAt'] = data.get('createdAt')
            if 'createdBy' in data:
                update_data['createdBy'] = data.get('createdBy')
            if 'utcOffset' in data:
                update_data['utcOffset'] = data.get('utcOffset')

            response = supabase.table('ecosuite_crm_customers').update(update_data).eq('id', customer_id).execute()

            if response.data:
                return Response({
                    "message": "CRM customer updated successfully",
                    "customer": response.data[0]
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to update CRM customer"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reservations(request):
    """Retrieve reservations with optional filters by brandId, outletId, status, etc."""
    supabase = create_supabase_client()
    try:
        # Get filter parameters from query string
        brand_id = request.query_params.get('brandId')
        outlet_id = request.query_params.get('outletId')
        reservation_status = request.query_params.get('status')
        table_id = request.query_params.get('tableId')
        customer_phone = request.query_params.get('customerPhone')
        reservation_id = request.query_params.get('id')
        
        # Build query
        query = supabase.table('ecosuite_reservations').select('*')
        
        # Apply filters
        if reservation_id:
            query = query.eq('id', reservation_id)
        if brand_id:
            query = query.eq('brandId', brand_id)
        if outlet_id:
            query = query.eq('outletId', outlet_id)
        if reservation_status:
            query = query.eq('status', reservation_status)
        if table_id:
            query = query.eq('tableId', table_id)
        if customer_phone:
            query = query.eq('customerPhone', customer_phone)
        
        # Execute query
        response = query.execute()
        reservations = response.data or []

        return Response({
            "reservations": reservations,
            "count": len(reservations)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_reservations_for_brand_with_reservation_id(request, brand_id, reservation_id):
    """Get reservations filtered by brandId and reservation id. Returns full JSON or empty list."""
    supabase = create_supabase_client()
    try:
        # Build query with filters for brandId and reservation id
        query = supabase.table('ecosuite_reservations').select('*')
        query = query.eq('brandId', brand_id)
        query = query.eq('id', reservation_id)
        
        # Execute query
        response = query.execute()
        reservations = response.data or []
        
        # Return the full JSON (list of reservations)
        return Response(reservations, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_reservations_for_brand(request, brand_id):
    """Get all reservations filtered by brandId. Returns latest data sorted in descending order by reservationDateTime."""
    supabase = create_supabase_client()
    try:
        # Build query with filter for brandId, sorted by reservationDateTime in descending order (latest first)
        query = supabase.table('ecosuite_reservations').select('*')
        query = query.eq('brandId', brand_id)
        query = query.order('reservationDateTime', desc=True)
        
        # Execute query
        response = query.execute()
        reservations = response.data or []
        
        # Return the full JSON (list of reservations)
        return Response(reservations, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_reservations_for_brand_with_phone_number(request, brand_id, phone_number):
    """Get reservations filtered by brandId and reservation id. Returns full JSON or empty list."""
    supabase = create_supabase_client()
    try:
        # Build query with filters for brandId and reservation id
        query = supabase.table('ecosuite_reservations').select('*')
        query = query.eq('brandId', brand_id)
        query = query.eq('customerPhone', phone_number)
        query = query.order('reservationDateTime', desc=True)
        
        # Execute query
        response = query.execute()
        reservations = response.data or []
        
        # Return the full JSON (list of reservations)
        return Response(reservations, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

def _format_full_date(reservation_datetime):
    """Format reservation datetime to full date format (e.g., 'Monday, January 15, 2024')."""
    try:
        if 'Z' in reservation_datetime:
            dt = datetime.fromisoformat(reservation_datetime.replace('Z', '+00:00'))
        elif '+' in reservation_datetime or reservation_datetime.count('-') > 2:
            dt = datetime.fromisoformat(reservation_datetime)
        else:
            dt = datetime.fromisoformat(reservation_datetime)
        return dt.strftime('%A, %B %d, %Y')
    except:
        return reservation_datetime

def _format_time_for_koala(reservation_datetime):
    """Format reservation datetime to time format for Koala (e.g., '7:00 PM')."""
    try:
        if 'Z' in reservation_datetime:
            dt = datetime.fromisoformat(reservation_datetime.replace('Z', '+00:00'))
        elif '+' in reservation_datetime or reservation_datetime.count('-') > 2:
            dt = datetime.fromisoformat(reservation_datetime)
        else:
            dt = datetime.fromisoformat(reservation_datetime)
        return dt.strftime('%I:%M %p').lstrip('0')
    except:
        return reservation_datetime

def _parse_phone_to_international(phone_number):
    """Parse phone number to international format. Handles Indonesian numbers starting with +62."""
    if not phone_number:
        return None
    
    phone_number = str(phone_number).strip()
    
    # If already in international format with +
    if phone_number.startswith('+'):
        return phone_number
    
    # If starts with +62 (Indonesian country code)
    if phone_number.startswith('+62'):
        return phone_number
    
    # If starts with 62 (without +)
    if phone_number.startswith('62'):
        return '+' + phone_number
    
    # If starts with 0 (Indonesian local format), convert to +62
    if phone_number.startswith('0'):
        return '+62' + phone_number[1:]
    
    # Default: assume Indonesian number and add +62
    return '+62' + phone_number

def _login_to_koala():
    """Login to Koala Plus and return access token."""
    try:
        trial_email = 'robin.dartanto@taratech.id'
        trial_password = 'TaraTech123'
        
        url = "https://api.koalaapp.id/v1/identity/auth/koala-plus/login"
        payload = json.dumps({
            "email": trial_email,
            "password": trial_password
        })
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        login_data = response.json()
        
        # Extract access token from response
        access_token = None
        if login_data.get('data') and login_data['data'].get('koalaToken'):
            access_token = login_data['data']['koalaToken'].get('accessToken')
        
        return access_token
    except Exception as e:
        print(f"Error logging in to Koala: {e}")
        return None

def _build_notification_data(reservations):
    """Build notification data array from a list of reservations."""
    notification_data = []
    
    for reservation in reservations:
        # Parse phone number
        customer_phone = reservation.get('customerPhone')
        if not customer_phone:
            continue
        
        phone_number_international = _parse_phone_to_international(customer_phone)
        if not phone_number_international:
            continue
        
        # Format date and time
        reservation_date_time = reservation.get('reservationDateTime')
        if not reservation_date_time:
            continue
        
        formatted_date = _format_full_date(reservation_date_time)
        formatted_time = _format_time_for_koala(reservation_date_time)
        pax = reservation.get('numberOfGuests', 0)
        reservation_id = reservation.get('id')
        
        # Prepare confirmation URL
        confirmation_url = f'https://taratechapi.fly.dev/api/ecosuite/confirm-reservation/{reservation_id}/'
        
        # Append notification data item
        notification_data.append({
            "phoneNumber": phone_number_international,
            "paramData": [
                f"*{pax}*",
                f"*{formatted_date}*",
                f"*{formatted_time}*",
                confirmation_url,
            ],
        })
    
    return notification_data

def _build_reminder_notification_data(reservations):
    """Build notification data array from a list of reservations for reminder messages.
    This function has different parameters than the reconfirmation notification data."""
    notification_data = []
    
    for reservation in reservations:
        # Parse phone number
        customer_phone = reservation.get('customerPhone')
        if not customer_phone:
            continue
        
        phone_number_international = _parse_phone_to_international(customer_phone)
        if not phone_number_international:
            continue
        
        # Format date and time
        reservation_date_time = reservation.get('reservationDateTime')
        if not reservation_date_time:
            continue
        
        formatted_date = _format_full_date(reservation_date_time)
        formatted_time = _format_time_for_koala(reservation_date_time)
        pax = reservation.get('numberOfGuests', 0)
        reservation_id = reservation.get('id')
        
        # Prepare confirmation URL
        confirmation_url = f'https://taratechapi.fly.dev/api/ecosuite/confirm-reservation/{reservation_id}/'
        
        # Append notification data item with different parameters for reminder template
        notification_data.append({
            "phoneNumber": phone_number_international,
            "paramData": [
                f"*{pax}*",
                f"*{formatted_date}*",
                f"*{formatted_time}*",
                # confirmation_url,
            ],
        })
    
    return notification_data

def _send_reconfirmation_broadcast(token, reservations, campaign_name='025', template_id='025'):
    """Send reconfirmation messages via Koala broadcast API for all reservations in a single request."""
    try:
        if not reservations:
            return {"success": False, "error": "No reservations provided"}
        
        # Build notification data for all reservations
        notification_data = _build_notification_data(reservations)
        
        if not notification_data:
            return {"success": False, "error": "No valid notification data could be built from reservations"}
        
        # Prepare broadcast payload
        broadcast_url = 'https://taratechapi.fly.dev/api/koalaplus/broadcast-reservation-success/'
        broadcast_payload = {
            'token': token,
            'campaignName': '025',
            'templateId': '025',
            'notificationData': notification_data,
        }
        
        # Send broadcast request
        broadcast_response = requests.post(
            broadcast_url,
            headers={'Content-Type': 'application/json'},
            json=broadcast_payload
        )
        
        if broadcast_response.status_code in [200, 201]:
            return {
                "success": True,
                "message": f"Reconfirmation messages sent successfully for {len(notification_data)} reservation(s)",
                "notifications_sent": len(notification_data)
            }
        else:
            return {
                "success": False,
                "error": f"Failed to send broadcast: {broadcast_response.status_code}",
                "response": broadcast_response.text
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

@api_view(['GET'])
@permission_classes([AllowAny])
def check_for_reservations_2_days_before_reservation_date(request):
    """Get all confirmed reservations that are scheduled 2 days from today. Compares only the date part, not the time.
    If reservations are found, automatically sends reconfirmation messages via Koala WhatsApp."""
    supabase = create_supabase_client()
    try:
        # Get today's date and calculate target date (2 days from now)
        today = timezone.localdate()
        target_date = today + timedelta(days=2)
        
        # Get all reservations from the database
        response = supabase.table('ecosuite_reservations').select('*').execute()
        all_reservations = response.data or []
        
        # Filter reservations where the date part matches the target date
        # 1-4 pax: confirmed reservations
        # 5+ pax: verified reservations
        matching_reservations_1_4_pax = []
        matching_reservations_5_plus_pax = []
        for reservation in all_reservations:
            reservation_status = reservation.get('status')
            reservation_date_time = reservation.get('reservationDateTime')
            if not reservation_date_time:
                continue
            
            try:
                # Parse the reservation datetime
                # Handle various ISO format variations
                reservation_dt = None
                if 'Z' in reservation_date_time:
                    reservation_dt = datetime.fromisoformat(reservation_date_time.replace('Z', '+00:00'))
                elif '+' in reservation_date_time or reservation_date_time.count('-') > 2:
                    reservation_dt = datetime.fromisoformat(reservation_date_time)
                else:
                    reservation_dt = datetime.fromisoformat(reservation_date_time)
                
                # Extract only the date part
                reservation_date = reservation_dt.date()
                
                # Check if the reservation date matches the target date (2 days from today)
                if reservation_date == target_date:
                    number_of_guests = reservation.get('numberOfGuests', 0)
                    try:
                        number_of_guests_int = int(number_of_guests) if number_of_guests else 0
                    except (ValueError, TypeError):
                        number_of_guests_int = 0
                    
                    # 1-4 pax: must be confirmed
                    if number_of_guests_int < 5:
                        if reservation_status == 'confirmed':
                            matching_reservations_1_4_pax.append(reservation)
                    # 5+ pax: must be verified
                    else:
                        if reservation_status == 'verified':
                            matching_reservations_5_plus_pax.append(reservation)
            except Exception as parse_error:
                # Skip reservations with invalid datetime format
                continue
        
        # Send reconfirmation messages for 1-4 pax (confirmed reservations)
        broadcast_result_1_4 = None
        if matching_reservations_1_4_pax:
            # Login to Koala to get token
            token = _login_to_koala()
            if not token:
                # Don't return early, continue to process 5+ pax group
                broadcast_result_1_4 = {"success": False, "error": "Failed to authenticate with Koala"}
            else:
                # Send reconfirmation messages for all reservations in a single broadcast
                broadcast_result_1_4 = _send_reconfirmation_broadcast(token, matching_reservations_1_4_pax, campaign_name='025', template_id='025')
        
        # Send reconfirmation messages for 5+ pax (verified reservations)
        broadcast_result_5_plus = None
        if matching_reservations_5_plus_pax:
            # Login to Koala to get token
            token = _login_to_koala()
            if not token:
                broadcast_result_5_plus = {"success": False, "error": "Failed to authenticate with Koala"}
            else:
                # Send reconfirmation messages for all reservations in a single broadcast
                broadcast_result_5_plus = _send_reconfirmation_broadcast(token, matching_reservations_5_plus_pax, campaign_name='028', template_id='028')
        
        # Determine if messages were sent successfully
        messages_sent_1_4 = len(matching_reservations_1_4_pax) > 0 and broadcast_result_1_4 and broadcast_result_1_4.get("success", False)
        messages_sent_5_plus = len(matching_reservations_5_plus_pax) > 0 and broadcast_result_5_plus and broadcast_result_5_plus.get("success", False)
        
        # Return the JSON of all matching reservations along with broadcast results
        return Response({
            "reservations": matching_reservations_1_4_pax + matching_reservations_5_plus_pax,
            "count": len(matching_reservations_1_4_pax) + len(matching_reservations_5_plus_pax),
            "reservations_1_4_pax": matching_reservations_1_4_pax,
            "count_1_4_pax": len(matching_reservations_1_4_pax),
            "reservations_5_plus_pax": matching_reservations_5_plus_pax,
            "count_5_plus_pax": len(matching_reservations_5_plus_pax),
            "broadcast_result_1_4_pax": broadcast_result_1_4,
            "broadcast_result_5_plus_pax": broadcast_result_5_plus,
            "messages_sent_1_4_pax": messages_sent_1_4,
            "messages_sent_5_plus_pax": messages_sent_5_plus,
            "messages_sent": messages_sent_1_4 or messages_sent_5_plus
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

def _send_reservation_reminder_broadcast(token, reservations, campaign_name='022', template_id='019'):
    """Send reservation reminder messages via Koala broadcast API for all reservations in a single request."""
    try:
        if not reservations:
            return {"success": False, "error": "No reservations provided"}
        
        # Build notification data for all reservations using reminder-specific function
        notification_data = _build_reminder_notification_data(reservations)
        
        if not notification_data:
            return {"success": False, "error": "No valid notification data could be built from reservations"}
        
        # Prepare broadcast payload
        broadcast_url = 'https://taratechapi.fly.dev/api/koalaplus/broadcast-reservation-success/'
        broadcast_payload = {
            'token': token,
            'campaignName': campaign_name,
            'templateId': template_id,
            'notificationData': notification_data,
        }
        
        # Send broadcast request
        broadcast_response = requests.post(
            broadcast_url,
            headers={'Content-Type': 'application/json'},
            json=broadcast_payload
        )
        
        if broadcast_response.status_code in [200, 201]:
            return {
                "success": True,
                "message": f"Reservation reminder messages sent successfully for {len(notification_data)} reservation(s)",
                "notifications_sent": len(notification_data)
            }
        else:
            return {
                "success": False,
                "error": f"Failed to send broadcast: {broadcast_response.status_code}",
                "response": broadcast_response.text
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

@api_view(['GET'])
@permission_classes([AllowAny])
def send_reservation_reminder_for_5pax_and_above_2day_before_reservation_date(request):
    """Get all pending reservations with 5+ pax that are scheduled 1 day from today. Compares only the date part, not the time.
    If reservations are found, automatically sends reminder messages via Koala WhatsApp."""
    supabase = create_supabase_client()
    try:
        # Get today's date and calculate target date (1 day from now)
        today = timezone.localdate()
        target_date = today + timedelta(days=1)
        
        # Get all reservations from the database
        response = supabase.table('ecosuite_reservations').select('*').execute()
        all_reservations = response.data or []
        
        # Filter reservations where the date part matches the target date, status is pending, and numberOfGuests >= 5
        matching_reservations = []
        for reservation in all_reservations:
            # Only process pending reservations
            reservation_status = reservation.get('status')
            if reservation_status == 'verified':
                continue
            
            # Only process reservations with 5 or more guests
            number_of_guests = reservation.get('numberOfGuests', 0)
            try:
                number_of_guests_int = int(number_of_guests) if number_of_guests else 0
                if number_of_guests_int < 5:
                    continue
            except (ValueError, TypeError):
                continue
            
            reservation_date_time = reservation.get('reservationDateTime')
            if not reservation_date_time:
                continue
            
            try:
                # Parse the reservation datetime
                # Handle various ISO format variations
                reservation_dt = None
                if 'Z' in reservation_date_time:
                    reservation_dt = datetime.fromisoformat(reservation_date_time.replace('Z', '+00:00'))
                elif '+' in reservation_date_time or reservation_date_time.count('-') > 2:
                    reservation_dt = datetime.fromisoformat(reservation_date_time)
                else:
                    reservation_dt = datetime.fromisoformat(reservation_date_time)
                
                # Extract only the date part
                reservation_date = reservation_dt.date()
                
                # Check if the reservation date matches the target date (1 day from today)
                if reservation_date == target_date:
                    matching_reservations.append(reservation)
            except Exception as parse_error:
                # Skip reservations with invalid datetime format
                continue
        
        # If list is not empty, send reminder messages
        broadcast_result = None
        if matching_reservations:
            # Login to Koala to get token
            token = _login_to_koala()
            if not token:
                return Response({
                    "reservations": matching_reservations,
                    "count": len(matching_reservations),
                    "message": "Reservations found but failed to authenticate with Koala. Messages not sent.",
                    "broadcast_result": None
                }, status=status.HTTP_200_OK)
            
            # Send reminder messages for all reservations in a single broadcast
            broadcast_result = _send_reservation_reminder_broadcast(token, matching_reservations, campaign_name='028', template_id='028')
        
        # Return the JSON of all matching reservations along with broadcast result
        return Response({
            "reservations": matching_reservations,
            "count": len(matching_reservations),
            "broadcast_result": broadcast_result,
            "messages_sent": len(matching_reservations) > 0 and broadcast_result and broadcast_result.get("success", False)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

def _build_cancel_notification_data(reservations):
    """Build notification data array from a list of reservations for cancel messages.
    Uses empty paramData since template 026 doesn't need parameters."""
    notification_data = []
    
    for reservation in reservations:
        # Parse phone number
        customer_phone = reservation.get('customerPhone')
        if not customer_phone:
            continue
        
        phone_number_international = _parse_phone_to_international(customer_phone)
        if not phone_number_international:
            continue
        
        # Append notification data item with empty paramData
        notification_data.append({
            "phoneNumber": phone_number_international,
            "paramData": [],
        })
    
    return notification_data

def _send_cancel_broadcast(token, reservations, campaign_name='026', template_id='026'):
    """Send cancel notification messages via Koala broadcast API for all reservations in a single request."""
    try:
        if not reservations:
            return {"success": False, "error": "No reservations provided"}
        
        # Build notification data for all reservations using cancel-specific function
        notification_data = _build_cancel_notification_data(reservations)
        
        if not notification_data:
            return {"success": False, "error": "No valid notification data could be built from reservations"}
        
        # Prepare broadcast payload
        broadcast_url = 'https://taratechapi.fly.dev/api/koalaplus/broadcast-reservation-success/'
        broadcast_payload = {
            'token': token,
            'campaignName': campaign_name,
            'templateId': template_id,
            'notificationData': notification_data,
        }
        
        # Send broadcast request
        broadcast_response = requests.post(
            broadcast_url,
            headers={'Content-Type': 'application/json'},
            json=broadcast_payload
        )
        
        if broadcast_response.status_code in [200, 201]:
            return {
                "success": True,
                "message": f"Cancel notification messages sent successfully for {len(notification_data)} reservation(s)",
                "notifications_sent": len(notification_data)
            }
        else:
            return {
                "success": False,
                "error": f"Failed to send broadcast: {broadcast_response.status_code}",
                "response": broadcast_response.text
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

@api_view(['GET'])
@permission_classes([AllowAny])
def send_cancel_notification_for_confirmed_reservations_1day_before_reservation_date(request):
    """Get all confirmed reservations where the reservation date is 1 day from today (tomorrow).
    Compares only the date part, not the time.
    If reservations are found, automatically sends cancel notification messages via Koala WhatsApp."""
    supabase = create_supabase_client()
    try:
        # Get today's date and calculate target date (1 day from today, i.e., tomorrow)
        today = timezone.localdate()
        target_date = today + timedelta(days=1)
        
        # Get all reservations from the database
        response = supabase.table('ecosuite_reservations').select('*').execute()
        all_reservations = response.data or []
        
        # Filter reservations where the date part matches the target date and status is confirmed
        matching_reservations = []
        for reservation in all_reservations:
            # Only process confirmed reservations
            reservation_status = reservation.get('status')
            if reservation_status != 'confirmed':
                continue
            
            reservation_date_time = reservation.get('reservationDateTime')
            if not reservation_date_time:
                continue
            
            try:
                # Parse the reservation datetime
                # Handle various ISO format variations
                reservation_dt = None
                if 'Z' in reservation_date_time:
                    reservation_dt = datetime.fromisoformat(reservation_date_time.replace('Z', '+00:00'))
                elif '+' in reservation_date_time or reservation_date_time.count('-') > 2:
                    reservation_dt = datetime.fromisoformat(reservation_date_time)
                else:
                    reservation_dt = datetime.fromisoformat(reservation_date_time)
                
                # Extract only the date part
                reservation_date = reservation_dt.date()
                
                # Check if the reservation date matches the target date (1 day from today)
                if reservation_date == target_date:
                    matching_reservations.append(reservation)
            except Exception as parse_error:
                # Skip reservations with invalid datetime format
                continue
        
        # If list is not empty, send cancel notification messages
        broadcast_result = None
        if matching_reservations:
            # Login to Koala to get token
            token = _login_to_koala()
            if not token:
                return Response({
                    "reservations": matching_reservations,
                    "count": len(matching_reservations),
                    "message": "Reservations found but failed to authenticate with Koala. Messages not sent.",
                    "broadcast_result": None
                }, status=status.HTTP_200_OK)
            
            # Send cancel notification messages for all reservations in a single broadcast
            broadcast_result = _send_cancel_broadcast(token, matching_reservations, campaign_name='026', template_id='026')
        
        # Return the JSON of all matching reservations along with broadcast result
        return Response({
            "reservations": matching_reservations,
            "count": len(matching_reservations),
            "broadcast_result": broadcast_result,
            "messages_sent": len(matching_reservations) > 0 and broadcast_result and broadcast_result.get("success", False)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_crm_customers(request):
    """Retrieve CRM customers with optional filters by brandId and outletId."""
    supabase = create_supabase_client()
    try:
        brand_id = request.query_params.get('brandId')
        outlet_id = request.query_params.get('outletId')

        query = supabase.table('ecosuite_crm_customers').select('*')
        if brand_id:
            query = query.eq('brandId', brand_id)
        if outlet_id:
            query = query.eq('outletId', outlet_id)

        response = query.execute()
        customers = response.data or []

        return Response({
            "customers": customers,
            "count": len(customers)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

def map_reservation_to_pivot_payment(reservation_data):
    """
    Map EcoSuiteReservation data to Pivot payment format.
    
    Args:
        reservation_data: The request data which may contain:
            - 'reservation': nested object with reservation fields
            - 'amount': payment amount
            - 'environment': staging/production
    
    Returns:
        Dictionary in Pivot payment format
    
    Raises:
        ValueError: If required fields are missing
    """
    # Check if reservation data is nested in a 'reservation' key
    reservation = reservation_data.get('reservation', {})
    if not reservation:
        # If no nested reservation, assume the data is flat
        reservation = reservation_data
    
    # Extract amount from top level (not from reservation object)
    amount = reservation_data.get('amount') or 0
    
    # Extract reservation fields from the reservation object
    reservation_id = (
        reservation.get('id') or 
        reservation.get('reservationId') or 
        reservation.get('clientReferenceId') or
        str(uuid.uuid4())  # Generate one if missing
    )
    
    customer_name = (
        reservation.get('customerName') or 
        reservation.get('customer_name') or
        ''
    )
    
    # Try multiple email field names
    email = (
        reservation.get('email') or 
        reservation.get('customerEmail') or
        reservation.get('customer_email') or
        ''
    )
    
    # Try multiple phone field names
    customer_phone = (
        reservation.get('customerPhone') or 
        reservation.get('customer_phone') or
        reservation.get('phone') or
        reservation.get('phoneNumber') or
        ''
    )
    
    number_of_guests = reservation.get('numberOfGuests') or reservation.get('number_of_guests') or 1
    notes = reservation.get('notes') or ''
    
    # Validate required fields
    if not customer_phone:
        raise ValueError("Customer phone is required. Please provide 'customerPhone' in the reservation data.")
    
    # Email might not be in reservation, generate a placeholder if missing
    # Pivot API requires email, so we'll use a format: phone@ecosuite.local
    if not email:
        # Generate email from phone number as fallback
        phone_clean = ''.join(filter(str.isdigit, customer_phone))
        email = f"{phone_clean}@ecosuite.local"
    
    if not reservation_id or reservation_id == '':
        reservation_id = str(uuid.uuid4())
    
    # Parse customer phone number (assuming format: +62XXXXXXXXXX or similar)
    phone_country_code = '+62'
    phone_number_raw = customer_phone.strip() if customer_phone else ''
    
    if not phone_number_raw:
        raise ValueError("Customer phone is required. Please provide 'customerPhone' in the reservation data.")
    
    # First, clean the phone number (remove spaces, dashes, parentheses, etc.)
    phone_number_cleaned = ''.join(filter(lambda c: c.isdigit() or c == '+', phone_number_raw))
    
    if phone_number_cleaned.startswith('+'):
        # Extract country code and number
        if phone_number_cleaned.startswith('+62'):
            phone_country_code = '+62'
            phone_number = phone_number_cleaned[3:]
        else:
            # Try to extract country code (could be +1, +44, etc.)
            # Find where the country code ends (usually 1-3 digits after +)
            digits_after_plus = ''
            for char in phone_number_cleaned[1:]:
                if char.isdigit():
                    digits_after_plus += char
                else:
                    break
            
            if digits_after_plus:
                # If we have digits, try to determine country code
                # For now, if it's not +62, we'll use what we found
                if phone_number_cleaned.startswith('+62'):
                    phone_country_code = '+62'
                    phone_number = phone_number_cleaned[3:]
                else:
                    # Use first 1-3 digits as country code
                    if len(digits_after_plus) >= 3:
                        phone_country_code = '+' + digits_after_plus[:3]
                        phone_number = phone_number_cleaned[4:]
                    elif len(digits_after_plus) >= 2:
                        phone_country_code = '+' + digits_after_plus[:2]
                        phone_number = phone_number_cleaned[3:]
                    else:
                        phone_country_code = '+' + digits_after_plus
                        phone_number = phone_number_cleaned[1 + len(digits_after_plus):]
            else:
                # No digits found, invalid format
                raise ValueError(f"Invalid phone number format: {customer_phone}. No digits found after +.")
    elif phone_number_cleaned.startswith('62'):
        # Phone starts with 62 (Indonesia country code without +)
        phone_country_code = '+62'
        phone_number = phone_number_cleaned[2:]
    elif phone_number_cleaned.startswith('0'):
        # Phone starts with 0 (local format), remove leading 0
        phone_country_code = '+62'
        phone_number = phone_number_cleaned[1:]
    else:
        # Just digits, assume Indonesia (+62)
        phone_country_code = '+62'
        phone_number = phone_number_cleaned
    
    # Final clean - remove any remaining non-digit characters
    phone_number = ''.join(filter(str.isdigit, phone_number))
    
    if not phone_number:
        raise ValueError(f"Invalid phone number format: {customer_phone}. Could not extract phone number.")
    
    # Validate phone number length (should be at least 8 digits for a valid phone number)
    if len(phone_number) < 8:
        raise ValueError(f"Invalid phone number: {customer_phone}. Phone number is too short (minimum 8 digits required).")
    
    # Extract payment amount and currency
    # Handle both formats: amount as number or amount as object with value/currency
    amount_value = amount
    amount_currency = 'IDR'
    
    # Build Pivot payment payload
    pivot_payment = {
        "clientReferenceId": reservation_id,
        "amount": {
            "value": amount_value,
            "currency": amount_currency
        },
        "paymentType": 'SINGLE',
        "mode": 'REDIRECT',
        "redirectUrl": {
            "successReturnUrl": "https://merchant.com/success",
            "failureReturnUrl": "https://merchant.com/failure",
            "expirationReturnUrl": "https://merchant.com/expiration",
        },
        "customer": {
            "givenName": customer_name.split(' ', 1)[0] if customer_name else '',
            "sureName": customer_name.split(' ', 1)[1] if ' ' in customer_name else customer_name,
            "email": email,
            "phoneNumber": {
                "countryCode": phone_country_code,
                "number": phone_number
            },
            "refundPreference": {
                "method": "AUTO"
            }
        },
        "orderInformation": {
            "productDetails": [
                {
                    "type": "SERVICE",
                    "category": "RESTAURANT",
                    "subCategory": "RESERVATION",
                    "name": f"Reservation for {number_of_guests} guests",
                    "description": notes or f"Table reservation",
                    "quantity": number_of_guests,
                    "price": {
                        "value": amount_value,
                        "currency": amount_currency
                    }
                }
            ]},
            "billingInfo": {
                "givenName": customer_name.split(' ', 1)[0] if customer_name else '',
                "sureName": customer_name.split(' ', 1)[1] if ' ' in customer_name else customer_name,
                "email": email,
                "phoneNumber": {
                    "countryCode": phone_country_code,
                    "number": phone_number
                
            },
            "shippingInfo": None
        },
        "autoConfirm": False,
        "statementDescriptor": 'EcoSuite Reservation',
        "expiryAt": None,
        "metadata": {
            "reservationId": reservation_id,
            "numberOfGuests": number_of_guests
        }
    }
    
    
    # Remove None values from nested structures
    def remove_none_values(obj):
        if isinstance(obj, dict):
            return {k: remove_none_values(v) for k, v in obj.items() if v is not None}
        elif isinstance(obj, list):
            return [remove_none_values(item) for item in obj if item is not None]
        return obj
    
    return remove_none_values(pivot_payment)


def authenticate_pivot_request(environment='staging'):
    """Authenticate a request to Pivot and return access token and base URL."""
    pivot_staging_url = 'https://api-stg.pivot-payment.com'
    pivot_production_url = 'https://api.pivot-payment.com'
    x_merchant_id = ''
    x_merchant_secret = ''

    if environment == 'staging':
        x_merchant_id = os.getenv('TARA_TECH_PIVOT_CLIENT_ID_STAGING')
        x_merchant_secret = os.getenv('TARA_TECH_PIVOT_CLIENT_SECRET_STAGING')
        base_url = pivot_staging_url
    elif environment == 'production':
        x_merchant_id = os.getenv('TARA_TECH_PIVOT_CLIENT_ID_PRODUCTION')
        x_merchant_secret = os.getenv('TARA_TECH_PIVOT_CLIENT_SECRET_PRODUCTION')
        base_url = pivot_production_url
    else:
        raise ValueError(f"Invalid environment: {environment}. Must be 'staging' or 'production'")

    if not x_merchant_id or not x_merchant_secret:
        raise ValueError(f"Missing Pivot credentials for {environment} environment")

    header = {
        'X-MERCHANT-ID': x_merchant_id,
        'X-MERCHANT-SECRET': x_merchant_secret,
    }
    body = {
        "grantType": "client_credentials"
    }

    response = requests.post(f'{base_url}/v1/access-token', headers=header, json=body)
    if response.status_code != 200:
        raise Exception(f"Failed to authenticate Pivot request: {response.status_code} - {response.text}")
    
    response_data = response.json()
    access_token = response_data.get('data', {}).get('accessToken')
    if not access_token:
        raise Exception("Access token not found in Pivot authentication response")
    
    return access_token, base_url

@api_view(['POST'])
@permission_classes([AllowAny])
def pivot_create_payment(request):
    """Create a payment in Pivot from EcoSuiteReservation data."""
    try:
        # Get the reservation data from request body
        reservation_data = request.data.copy()
        
        # Extract environment (needed for authentication)
        environment = reservation_data.get('environment', 'staging')
        
        # Validate that we have the minimum required data
        if not reservation_data:
            return Response({
                "error": "Request body is empty. Please provide reservation data."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate with Pivot to get access token
        pivot_access_token, base_url = authenticate_pivot_request(environment)
        
        # Map reservation data to Pivot payment format
        # This will raise ValueError if required fields are missing
        pivot_payment_payload = map_reservation_to_pivot_payment(
            reservation_data
        )
        
        # Double-check required fields before sending
        if not pivot_payment_payload.get('clientReferenceId'):
            return Response({
                "error": "clientReferenceId is required but was not generated. Please provide 'id' in reservation data.",
                "received_data_keys": list(reservation_data.keys())
            }, status=status.HTTP_400_BAD_REQUEST)
        
        customer_info = pivot_payment_payload.get('customer', {})
        if not customer_info.get('email'):
            return Response({
                "error": "Customer email is required. Please provide 'email' or 'customerEmail' in reservation data.",
                "received_data_keys": list(reservation_data.keys())
            }, status=status.HTTP_400_BAD_REQUEST)
        
        phone_info = customer_info.get('phoneNumber', {})
        if not phone_info.get('number'):
            return Response({
                "error": "Customer phone number is required. Please provide 'customerPhone' in reservation data.",
                "received_data_keys": list(reservation_data.keys())
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare headers for the payment creation request
        headers = {
            'Authorization': f'Bearer {pivot_access_token}',
            'Content-Type': 'application/json'
        }
        
        # Make POST request to Pivot API to create payment
        pivot_response = requests.post(
            f'{base_url}/v2/payments',
            headers=headers,
            json=pivot_payment_payload
        )
        
        # Return the response from Pivot API
        if pivot_response.status_code in [200, 201]:
            return Response({
                "message": "Payment created successfully",
                "data": pivot_response.json()
            }, status=status.HTTP_200_OK)
        else:
            try:
                error_response = pivot_response.json()
            except:
                error_response = pivot_response.text
            
            return Response({
                "error": "Failed to create payment in Pivot",
                "status_code": pivot_response.status_code,
                "response": error_response,
                "request_payload": pivot_payment_payload,
                "received_reservation_keys": list(reservation_data.keys())
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except ValueError as e:
        return Response({
            "error": str(e),
            "received_data_keys": list(request.data.keys()) if hasattr(request, 'data') else []
        }, status=status.HTTP_400_BAD_REQUEST)
    except KeyError as e:
        return Response({
            "error": f"Missing required field: {str(e)}",
            "received_data_keys": list(request.data.keys()) if hasattr(request, 'data') else []
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "error": str(e),
            "error_type": type(e).__name__,
            "received_data_keys": list(request.data.keys()) if hasattr(request, 'data') else []
        }, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([AllowAny])
def pivot_check_payment(request, reservation_id):
    """Check payment status for a specific reservation from Pivot API."""
    try:
        supabase = create_supabase_client()
        
        # Get environment from query params or default to staging
        environment = request.query_params.get('environment', 'staging')
        
        # Get reservation from Supabase
        reservation_response = supabase.table('ecosuite_reservations').select('*').eq('id', reservation_id).execute()
        
        if not reservation_response.data or len(reservation_response.data) == 0:
            return Response({
                "error": f"Reservation with id {reservation_id} not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        reservation = reservation_response.data[0]
        payments = reservation.get('payments', [])
        
        if not payments or len(payments) == 0:
            return Response({
                "error": f"No payments found for reservation {reservation_id}",
                "reservation": reservation
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Filter to only pending payments
        pending_payments = [p for p in payments if p.get('status', '').lower() == 'pending']
        
        if not pending_payments:
            return Response({
                "message": "No pending payments found for this reservation",
                "reservation": reservation
            }, status=status.HTTP_200_OK)
        
        # Authenticate with Pivot
        pivot_access_token, base_url = authenticate_pivot_request(environment)
        
        # Check status for each pending payment
        updated_payments = []
        payment_statuses = []
        
        # Create a map of payment IDs to payments for easy lookup
        payment_map = {p.get('id'): p for p in payments}
        
        for payment in pending_payments:
            payment_id = payment.get('id')
            if not payment_id:
                continue
            
            # Get payment status from Pivot API
            headers = {
                'Authorization': f'Bearer {pivot_access_token}',
                'Content-Type': 'application/json'
            }
            
            pivot_response = requests.get(
                f'{base_url}/v2/payments/{payment_id}',
                headers=headers
            )
            
            if pivot_response.status_code == 200:
                pivot_data = pivot_response.json()
                pivot_payment = pivot_data.get('data', {})
                
                # Map Pivot status to our status
                # Pivot statuses: SUCCESS, EXPIRED, FAILED, PROCESSING, WAITING_FOR_USER_ACTION, 
                # WAITING_FOR_AUTHENTICATION, WAITING_FOR_CAPTURE
                pivot_status = pivot_payment.get('status', '').upper()
                if pivot_status == 'SUCCESS':
                    new_status = 'paid'
                    paid_at = pivot_payment.get('paidAt') or pivot_payment.get('settledAt') or timezone.now().isoformat()
                    payment['paidAt'] = paid_at
                elif pivot_status == 'EXPIRED':
                    new_status = 'expired'
                elif pivot_status == 'FAILED':
                    new_status = 'cancelled'
                elif pivot_status == 'PROCESSING':
                    new_status = 'processing'
                else:
                    # WAITING_FOR_USER_ACTION, WAITING_FOR_AUTHENTICATION, WAITING_FOR_CAPTURE, etc.
                    new_status = 'pending'
                
                # Update payment status
                payment['status'] = new_status
                payment['updatedAt'] = timezone.now().isoformat()
                
                # Update in payment map
                payment_map[payment_id] = payment
                
                payment_statuses.append({
                    'paymentId': payment_id,
                    'status': new_status,
                    'pivotStatus': pivot_status,
                    'pivotData': pivot_payment
                })
            else:
                # If payment not found in Pivot, mark as expired or keep current status
                if pivot_response.status_code == 404:
                    payment['status'] = 'expired'
                    payment['updatedAt'] = timezone.now().isoformat()
                    payment_map[payment_id] = payment
                    payment_statuses.append({
                        'paymentId': payment_id,
                        'status': 'expired',
                        'error': 'Payment not found in Pivot'
                    })
                else:
                    payment_statuses.append({
                        'paymentId': payment_id,
                        'status': payment.get('status', 'pending'),
                        'error': f'Failed to check status: {pivot_response.status_code}'
                    })
        
        # Rebuild payments array with updated statuses
        updated_payments = list(payment_map.values())
        
        # Update reservation with updated payments
        reservation['payments'] = updated_payments
        reservation['updatedAt'] = timezone.now().isoformat()
        reservation['updatedBy'] = request.user.id
        
        update_response = supabase.table('ecosuite_reservations').update({
            'payments': updated_payments,
            'updatedAt': reservation['updatedAt'],
            'updatedBy': reservation['updatedBy']
        }).eq('id', reservation_id).execute()
        
        if update_response.data:
            return Response({
                "message": "Payment status checked and updated successfully",
                "reservation": update_response.data[0],
                "paymentStatuses": payment_statuses
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "Payment status checked but failed to update reservation",
                "paymentStatuses": payment_statuses,
                "error": "Failed to update reservation in database"
            }, status=status.HTTP_200_OK)
            
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "error": str(e),
            "error_type": type(e).__name__
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pivot_check_all_pending_payments(request):
    """Check all pending payments and update their status."""
    try:
        supabase = create_supabase_client()
        
        # Get environment from request body or default to staging
        environment = request.data.get('environment', 'staging')
        
        # Get all reservations with pending payments
        all_reservations_response = supabase.table('ecosuite_reservations').select('*').execute()
        
        if not all_reservations_response.data:
            return Response({
                "message": "No reservations found",
                "updated": 0
            }, status=status.HTTP_200_OK)
        
        # Authenticate with Pivot once
        pivot_access_token, base_url = authenticate_pivot_request(environment)
        headers = {
            'Authorization': f'Bearer {pivot_access_token}',
            'Content-Type': 'application/json'
        }
        
        updated_count = 0
        error_count = 0
        results = []
        
        # Process each reservation
        for reservation in all_reservations_response.data:
            payments = reservation.get('payments', [])
            if not payments:
                continue
            
            # Filter to only pending payments
            pending_payments = [p for p in payments if p.get('status', '').lower() == 'pending']
            
            # Create a map of payment IDs to payments for easy lookup
            payment_map = {p.get('id'): p for p in payments}
            
            # Check each pending payment (if any)
            for payment in pending_payments:
                payment_id = payment.get('id')
                
                if not payment_id:
                    continue
                
                try:
                    # Get payment status from Pivot API
                    pivot_response = requests.get(
                        f'{base_url}/v2/payments/{payment_id}',
                        headers=headers
                    )
                    
                    if pivot_response.status_code == 200:
                        pivot_data = pivot_response.json()
                        pivot_payment = pivot_data.get('data', {})
                        
                        # Map Pivot status to our status
                        # Pivot statuses: SUCCESS, EXPIRED, FAILED, PROCESSING, WAITING_FOR_USER_ACTION, 
                        # WAITING_FOR_AUTHENTICATION, WAITING_FOR_CAPTURE
                        pivot_status = pivot_payment.get('status', '').upper()
                        if pivot_status == 'SUCCESS':
                            new_status = 'paid'
                            paid_at = pivot_payment.get('paidAt') or pivot_payment.get('settledAt') or timezone.now().isoformat()
                            payment['paidAt'] = paid_at
                        elif pivot_status == 'EXPIRED':
                            new_status = 'expired'
                        elif pivot_status == 'FAILED':
                            new_status = 'cancelled'
                        elif pivot_status == 'PROCESSING':
                            new_status = 'processing'
                        else:
                            # WAITING_FOR_USER_ACTION, WAITING_FOR_AUTHENTICATION, WAITING_FOR_CAPTURE, etc.
                            new_status = 'pending'
                        
                        # Update payment
                        payment['status'] = new_status
                        payment['updatedAt'] = timezone.now().isoformat()
                        
                        # Update in payment map
                        payment_map[payment_id] = payment
                        
                        results.append({
                            'reservationId': reservation.get('id'),
                            'paymentId': payment_id,
                            'oldStatus': 'pending',
                            'newStatus': new_status,
                            'pivotStatus': pivot_status
                        })
                    elif pivot_response.status_code == 404:
                        # Payment not found in Pivot, mark as expired
                        payment['status'] = 'expired'
                        payment['updatedAt'] = timezone.now().isoformat()
                        payment_map[payment_id] = payment
                        results.append({
                            'reservationId': reservation.get('id'),
                            'paymentId': payment_id,
                            'oldStatus': 'pending',
                            'newStatus': 'expired',
                            'pivotStatus': 'NOT_FOUND'
                        })
                    else:
                        # Error checking payment, keep as pending
                        error_count += 1
                        results.append({
                            'reservationId': reservation.get('id'),
                            'paymentId': payment_id,
                            'oldStatus': 'pending',
                            'newStatus': 'pending',
                            'error': f'Failed to check: {pivot_response.status_code}'
                        })
                    
                except Exception as e:
                    error_count += 1
                    results.append({
                        'reservationId': reservation.get('id'),
                        'paymentId': payment_id,
                        'error': str(e)
                    })
            
            # Rebuild payments array with updated statuses
            updated_payments = list(payment_map.values())
            has_successful_payment = any(
                p.get('status', '').lower() == 'paid'
                for p in updated_payments
            )
            reservation_status = reservation.get('status', '').lower()
            should_confirm_reservation = (
                has_successful_payment and
                reservation_status in ['pending', 'unpaid']
            )
            
            # Update reservation with updated payments (and status when needed)
            try:
                reservation['payments'] = updated_payments
                reservation['updatedAt'] = timezone.now().isoformat()
                reservation['updatedBy'] = request.user.id
                update_payload = {
                    'payments': updated_payments,
                    'updatedAt': reservation['updatedAt'],
                    'updatedBy': reservation['updatedBy']
                }
                
                if should_confirm_reservation:
                    reservation['status'] = 'confirmed'
                    update_payload['status'] = 'confirmed'
                
                update_response = supabase.table('ecosuite_reservations').update(update_payload).eq('id', reservation.get('id')).execute()
                
                if update_response.data:
                    updated_count += 1
            except Exception as e:
                error_count += 1
                results.append({
                    'reservationId': reservation.get('id'),
                    'error': f'Failed to update reservation: {str(e)}'
                })
        
        return Response({
            "message": "Pending payments checked and updated",
            "updatedReservations": updated_count,
            "errors": error_count,
            "results": results
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "error": str(e),
            "error_type": type(e).__name__
        }, status=status.HTTP_400_BAD_REQUEST)

def check_reservation_conflicts(supabase, brand_id, outlet_id, reservation_date_time):
    """
    Check if there are any 'on hold' reservations within 2 hours before or after the requested time.
    
    Args:
        supabase: Supabase client instance
        brand_id: Brand ID to check
        outlet_id: Outlet ID to check
        reservation_date_time: ISO format datetime string
    
    Returns:
        True if conflicts exist (should be waitlisted), False if no conflicts (should be pending)
    """
    try:
        from datetime import datetime, timedelta
        
        # Parse the requested reservation datetime
        # Handle various ISO format variations
        requested_dt = None
        try:
            # Try parsing with timezone info
            if 'Z' in reservation_date_time:
                requested_dt = datetime.fromisoformat(reservation_date_time.replace('Z', '+00:00'))
            elif '+' in reservation_date_time or reservation_date_time.count('-') > 2:
                requested_dt = datetime.fromisoformat(reservation_date_time)
            else:
                # No timezone info, treat as naive datetime
                requested_dt = datetime.fromisoformat(reservation_date_time)
        except Exception as parse_error:
            print(f"Error parsing datetime: {parse_error}")
            return False
        
        if not requested_dt:
            return False
        
        # Calculate time range (2 hours before and after)
        time_before = requested_dt - timedelta(hours=2)
        time_after = requested_dt + timedelta(hours=2)
        
        # Convert back to ISO format for database query
        time_before_iso = time_before.isoformat()
        time_after_iso = time_after.isoformat()
        
        # Query for active reservations in the time range (exclude pending and cancelled)
        response = supabase.table('ecosuite_reservations').select('*').eq('brandId', brand_id).eq('outletId', outlet_id).in_('status', ['waitlisted', 'confirmed', 'verified']).gte('reservationDateTime', time_before_iso).lte('reservationDateTime', time_after_iso).execute()
        
        # If any on hold reservations exist in this time range, return True (conflict exists)
        if response.data and len(response.data) > 0:
            return True
        
        return False
        
    except Exception as e:
        print(f"Error checking reservation conflicts: {e}")
        # If there's an error, default to no conflict (pending)
        return False

def _get_max_pax_from_operating_hours(outlet, reservation_date):
    """
    Get maxPax for a specific date from outlet's operating hours.
    Prioritizes date exceptions over day-based hours.
    Returns None if no maxPax is configured (date is unavailable).
    """
    if not outlet:
        return None
    
    online_hours = outlet.get('onlineOperatingHours', {})
    if not online_hours:
        return None
    
    # Get date exceptions and day-based hours
    date_exceptions = online_hours.get('dateExceptions', [])
    day_based_hours = online_hours.get('dayBasedHours', [])
    
    # Format reservation date as YYYY-MM-DD
    date_str = reservation_date.strftime('%Y-%m-%d')
    
    # Check date exceptions first (prioritize over day-based hours)
    for exception in date_exceptions:
        if exception.get('date') == date_str:
            # If date is closed, return None (unavailable)
            if exception.get('isClosed', False):
                return None
            # Return maxPax from date exception
            max_pax = exception.get('maxPax')
            if max_pax is not None:
                return max_pax
    
    # If no date exception found, check day-based hours
    # Get day of week - JavaScript convention: 0 = Sunday, 1 = Monday, ..., 6 = Saturday
    # Python weekday(): 0 = Monday, 1 = Tuesday, ..., 6 = Sunday
    # Convert Python weekday to JavaScript day: (weekday + 1) % 7
    python_weekday = reservation_date.weekday()  # Monday=0, Sunday=6
    js_day = (python_weekday + 1) % 7  # Sunday=0, Monday=1, ..., Saturday=6
    
    for day_hour in day_based_hours:
        if day_hour.get('day') == js_day:
            max_pax = day_hour.get('maxPax')
            if max_pax is not None:
                return max_pax
    
    # No maxPax configured for this date
    return None

def _round_to_nearest_even(number):
    """Round a number up to the nearest even number."""
    import math
    return math.ceil((number + 1) / 2) * 2

@api_view(['GET'])
@permission_classes([AllowAny])
def check_reservation_availability(request):
    """
    Check reservation availability without creating a reservation.
    Returns conflict information to help user decide whether to join waitlist or pick another time.
    
    New Rules:
    1. Check isMaxPaxExclusive flag - if true, only count reservations with createdBy == 'website'
    2. Get maxPax from operating hours (prioritize date exceptions over day-based hours)
    3. Filter reservations within 2-hour window (status not pending/cancelled)
    4. Calculate current total pax and round to nearest even number
    5. Check if (roundedCurrentPax + newGuests) > maxPax
    
    Query parameters:
    - brandId: Brand ID (required)
    - outletId: Outlet ID (required)
    - dateTime: Reservation date and time in ISO format (required)
    - guests: Number of guests (required for capacity checks)
    """
    supabase = create_supabase_client()
    try:
        # Get query parameters
        brand_id = request.query_params.get('brandId')
        outlet_id = request.query_params.get('outletId')
        reservation_date_time = request.query_params.get('dateTime')
        number_of_guests = request.query_params.get('guests')
        
        # Validate required fields
        if not brand_id:
            return Response({
                "error": "Brand ID is required",
                "parameter": "brandId"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not outlet_id:
            return Response({
                "error": "Outlet ID is required",
                "parameter": "outletId"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not reservation_date_time:
            return Response({
                "error": "Reservation date and time is required",
                "parameter": "dateTime"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate guests parameter
        if not number_of_guests:
            return Response({
                "error": "Number of guests is required",
                "parameter": "guests"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            number_of_guests = int(number_of_guests)
        except (ValueError, TypeError):
            return Response({
                "error": "Number of guests must be a valid number",
                "parameter": "guests"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize the dateTime format
        if reservation_date_time:
            # Replace space before timezone offset with +
            reservation_date_time = re.sub(r'(\d{2}:\d{2}:\d{2})\s+(\d{2}:\d{2})$', r'\1+\2', reservation_date_time)
            
            # Validate datetime format
            iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$'
            if not re.match(iso_pattern, reservation_date_time):
                return Response({
                    "error": "Invalid date/time format. Please use ISO 8601 format (e.g., 2025-11-18T18:00:00+07:00 or 2025-11-18T18:00:00Z)",
                    "parameter": "dateTime",
                    "received_value": reservation_date_time
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get brand data to access outlet's operating hours
        brand_response = supabase.table('ecosuite_brands').select('*').eq('id', brand_id).execute()
        if not brand_response.data or len(brand_response.data) == 0:
            return Response({
                "error": "Brand not found",
                "parameter": "brandId"
            }, status=status.HTTP_404_NOT_FOUND)
        
        brand = brand_response.data[0]
        outlets = brand.get('outlets', [])
        outlet = None
        for out in outlets:
            if out.get('id') == outlet_id:
                outlet = out
                break
        
        if not outlet:
            return Response({
                "error": "Outlet not found",
                "parameter": "outletId"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Parse reservation datetime
        try:
            dt = datetime.fromisoformat(reservation_date_time.replace('Z', '+00:00'))
            reservation_date = dt.date()
            time_before = dt - timedelta(hours=2)
            time_after = dt + timedelta(hours=2)
        except Exception as e:
            return Response({
                "error": "Invalid date/time format",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get maxPax from operating hours
        max_pax = _get_max_pax_from_operating_hours(outlet, reservation_date)
        if max_pax is None:
            return Response({
                "available": False,
                "hasConflicts": True,
                "hasCapacityConflict": True,
                "conflictReason": ["no_max_pax_configured"],
                "message": "This date is unavailable. No maximum capacity is configured for this date.",
                "requestedDateTime": reservation_date_time,
                "requestedGuests": number_of_guests,
                "maxPax": None
            }, status=status.HTTP_200_OK)
        
        # Get isMaxPaxExclusive flag
        online_hours = outlet.get('onlineOperatingHours', {})
        is_max_pax_exclusive = online_hours.get('isMaxPaxExclusive', False)
        
        # Fetch existing reservations in the 2-hour window
        # Filter: match outlet, status not pending/cancelled, within time window
        query = supabase.table('ecosuite_reservations').select('*').eq('brandId', brand_id).eq('outletId', outlet_id).not_.in_('status', ['pending', 'cancelled']).gte('reservationDateTime', time_before.isoformat()).lte('reservationDateTime', time_after.isoformat())
        
        # If exclusive, only count reservations with createdBy == 'website'
        if is_max_pax_exclusive:
            query = query.eq('createdBy', 'website')
        
        response = query.execute()
        conflicting_reservations = response.data or []
        
        # Calculate current total pax from filtered reservations
        total_existing_pax = 0
        for reservation in conflicting_reservations:
            guests = reservation.get('numberOfGuests', 0)
            try:
                guests_int = int(guests) if guests else 0
                total_existing_pax += guests_int
            except (ValueError, TypeError):
                pass
        
        # Round current total pax to nearest even number
        rounded_current_pax = _round_to_nearest_even(total_existing_pax)
        
        # Check capacity with new reservation
        total_with_new = rounded_current_pax + number_of_guests
        has_capacity_conflict = total_with_new > max_pax
        
        # Build response
        conflict_reason = []
        if has_capacity_conflict:
            conflict_reason.append("capacity_exceeded")
        
        if has_capacity_conflict:
            message = f"Capacity limit reached. Current: {rounded_current_pax} pax (rounded from {total_existing_pax} pax), max: {max_pax} pax. Your request for {number_of_guests} pax would result in {total_with_new} pax, exceeding the limit. You can join the waitlist."
        else:
            message = "Reservations available for this time slot"
        
        return Response({
            "available": not has_capacity_conflict,
            "hasConflicts": has_capacity_conflict,
            "hasTimeConflicts": False,  # Time conflicts are now part of capacity check
            "hasCapacityConflict": has_capacity_conflict,
            "conflictReason": conflict_reason,
            "requestedDateTime": reservation_date_time,
            "requestedGuests": number_of_guests,
            "totalExistingPax": total_existing_pax,
            "roundedCurrentPax": rounded_current_pax,
            "totalWithNew": total_with_new,
            "maxPax": max_pax,
            "isMaxPaxExclusive": is_max_pax_exclusive,
            "conflictingReservations": len(conflicting_reservations),
            "message": message,
            "recommendedStatus": "waitlisted" if has_capacity_conflict else "pending",
            "suggestedAction": None if not has_capacity_conflict else "join_waitlist_or_choose_another_time"
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "error": str(e),
            "error_type": type(e).__name__
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def request_reservation(request):
    """
    Create a reservation request via query parameters.
    Accessible from anywhere (website, Instagram, etc.) without authentication.
    
    The flow now requires checking availability first, then user decides on action.
    
    Query parameters:
    - name: Customer name (required)
    - phone: International phone number (required) - automatically normalized
    - guests: Number of guests (required)
    - dateTime: Reservation date and time in ISO format (required) - automatically normalized
    - notes: Additional notes (optional)
    - brandId: Brand ID (required)
    - outletId: Outlet ID (required)
    - joinWaitlist: "true" or "false" (required if conflicts exist)
    """
    supabase = create_supabase_client()
    try:
        # Get query parameters
        customer_name = request.query_params.get('name')
        customer_phone = request.query_params.get('phone')
        number_of_guests = request.query_params.get('guests')
        reservation_date_time = request.query_params.get('dateTime')
        notes = request.query_params.get('notes', '')
        brand_id = request.query_params.get('brandId')
        outlet_id = request.query_params.get('outletId')
        created_by = request.query_params.get('createdBy', 'website')
        updated_by = request.query_params.get('updatedBy', 'website')
        reservation_payments = request.query_params.get('payments', [])
        
        # Validate required fields
        if not customer_name:
            return Response({
                "error": "Customer name is required",
                "parameter": "name"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not customer_phone:
            return Response({
                "error": "Customer phone is required",
                "parameter": "phone"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize phone number - handle case where + becomes a space after URL decoding
        if customer_phone:
            customer_phone = customer_phone.strip()
            # If phone starts with a space followed by digits, it's likely a + that got decoded
            if customer_phone.startswith(' ') and len(customer_phone) > 1 and customer_phone[1].isdigit():
                customer_phone = '+' + customer_phone[1:]
            # Also handle case where there's no + at all (add it if it starts with digits)
            elif customer_phone and customer_phone[0].isdigit():
                # If it starts with country code like 62, 1, 44, etc., add +
                customer_phone = '+' + customer_phone
        
        if not number_of_guests:
            return Response({
                "error": "Number of guests is required",
                "parameter": "guests"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not reservation_date_time:
            return Response({
                "error": "Reservation date and time is required",
                "parameter": "dateTime"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not brand_id:
            return Response({
                "error": "Brand ID is required",
                "parameter": "brandId"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not outlet_id:
            return Response({
                "error": "Outlet ID is required",
                "parameter": "outletId"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Convert number of guests to integer
        try:
            number_of_guests = int(number_of_guests)
        except ValueError:
            return Response({
                "error": "Number of guests must be a valid number",
                "parameter": "guests"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize the dateTime format
        # Handle case where + in timezone becomes a space after URL decoding
        if reservation_date_time:
            # Replace space before timezone offset with +
            # This handles "2025-11-18T18:00:00 07:00" -> "2025-11-18T18:00:00+07:00"
            reservation_date_time = re.sub(r'(\d{2}:\d{2}:\d{2})\s+(\d{2}:\d{2})$', r'\1+\2', reservation_date_time)
            
            # Basic validation - check if it looks like an ISO datetime
            # Accept formats like: 2025-11-18T18:00:00Z, 2025-11-18T18:00:00+07:00, 2025-11-18T18:00:00.000Z
            iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$'
            if not re.match(iso_pattern, reservation_date_time):
                return Response({
                    "error": "Invalid date/time format. Please use ISO 8601 format (e.g., 2025-11-18T18:00:00+07:00 or 2025-11-18T18:00:00Z)",
                    "parameter": "dateTime",
                    "received_value": reservation_date_time
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate reservation ID
        reservation_id = str(uuid.uuid4())
        now = timezone.now().isoformat()
        
        # Check for conflicting reservations
        has_conflicts = check_reservation_conflicts(supabase, brand_id, outlet_id, reservation_date_time)
        
        # Get joinWaitlist parameter
        join_waitlist_param = request.query_params.get('joinWaitlist', '').lower()
        
        # Determine status based on conflicts and user choice
        if has_conflicts:
            # If conflicts exist, user must explicitly choose to join waitlist or not
            if join_waitlist_param == '':
                # No choice provided, ask user to decide
                return Response({
                    "error": "Conflict detected",
                    "message": "There are existing reservations within 2 hours of your requested time. Please choose an action.",
                    "hasConflicts": True,
                    "requestedDateTime": reservation_date_time,
                    "actions": {
                        "joinWaitlist": "Add '&joinWaitlist=true' to join the waitlist",
                        "chooseAnotherTime": "Add '&joinWaitlist=false' or select a different time"
                    },
                    "suggestedAction": "Please use the check-reservation-availability endpoint first to see availability"
                }, status=status.HTTP_409_CONFLICT)
            elif join_waitlist_param == 'true':
                # User chose to join waitlist
                reservation_status = 'waitlisted'
            elif join_waitlist_param == 'false':
                # User chose not to join waitlist
                return Response({
                    "error": "Reservation not created",
                    "message": "You chose not to join the waitlist. Please select a different time for your reservation.",
                    "hasConflicts": True,
                    "requestedDateTime": reservation_date_time,
                    "suggestion": "Use the check-reservation-availability endpoint to find available times"
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "error": "Invalid joinWaitlist parameter",
                    "message": "joinWaitlist must be 'true' or 'false'",
                    "received_value": join_waitlist_param
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # No conflicts, create with pending status
            reservation_status = 'pending'
        
        # Create reservation data
        reservation_data = {
            'id': reservation_id,
            'brandId': brand_id,
            'outletId': outlet_id,
            'customerName': customer_name,
            'customerPhone': customer_phone,
            'numberOfGuests': number_of_guests,
            'reservationDateTime': reservation_date_time,
            'status': reservation_status,
            'notes': notes,
            'createdAt': now,
            'updatedAt': now,
            'payments': reservation_payments,
            'tableId': None,
            'checkedInAt': None,
            'checkedInBy': None,
            'checkedOutAt': None,
            'checkedOutBy': None,
            'createdBy': created_by,
            'updatedBy': updated_by,
        }
        
        # Insert reservation into Supabase
        response = supabase.table('ecosuite_reservations').insert(reservation_data).execute()
        
        if response.data:
            return Response({
                "message": "Reservation request created successfully",
                "reservation": response.data[0]
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "error": "Failed to create reservation request"
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            "error": str(e),
            "error_type": type(e).__name__
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def confirm_reservation(request, reservation_id):
    """
    Confirmation endpoint for customers to confirm or cancel their reservation.
    Accessible via link sent through email or messaging service.
    
    GET: Display confirmation UI
    POST or GET with action parameter: Process confirmation/cancellation
    
    Query parameters:
    - action: "confirm" or "cancel" (optional, triggers action)
    """
    supabase = create_supabase_client()
    
    try:
        # Get the reservation
        response = supabase.table('ecosuite_reservations').select('*').eq('id', reservation_id).execute()
        
        if not response.data or len(response.data) == 0:
            return render(request, 'ecosuite/reservation_error.html', {
                'error_title': 'Reservation not found',
                'error_message': "The reservation you're looking for doesn't exist."
            })
        
        reservation = response.data[0]
        
        # Format datetime for display
        formatted_datetime = format_reservation_datetime(reservation.get('reservationDateTime', 'N/A'))
        
        # Check if action is provided (either as query param or POST data)
        action = None
        if request.method == 'POST':
            action = request.data.get('action') or request.POST.get('action')
        elif request.method == 'GET':
            action = request.query_params.get('action')
        
        # If action is provided, process it
        if action:
            if action.lower() == 'confirm':
                # Update reservation status to confirmed
                update_data = {
                    'status': 'confirmed',
                    'updatedAt': timezone.now().isoformat()
                }
                update_response = supabase.table('ecosuite_reservations').update(update_data).eq('id', reservation_id).execute()
                
                if update_response.data:
                    updated_reservation = update_response.data[0]
                    formatted_datetime_updated = format_reservation_datetime(updated_reservation.get('reservationDateTime', 'N/A'))
                    return render(request, 'ecosuite/reservation_success.html', {
                        'reservation': updated_reservation,
                        'formatted_datetime': formatted_datetime_updated,
                        'action': 'confirmed'
                    })
                else:
                    return render(request, 'ecosuite/reservation_error.html', {
                        'error_title': 'Update Failed',
                        'error_message': 'Failed to confirm the reservation. Please try again.'
                    })
                    
            elif action.lower() == 'cancel':
                # Update reservation status to cancelled
                update_data = {
                    'status': 'cancelled',
                    'updatedAt': timezone.now().isoformat()
                }
                update_response = supabase.table('ecosuite_reservations').update(update_data).eq('id', reservation_id).execute()
                
                if update_response.data:
                    updated_reservation = update_response.data[0]
                    formatted_datetime_updated = format_reservation_datetime(updated_reservation.get('reservationDateTime', 'N/A'))
                    return render(request, 'ecosuite/reservation_success.html', {
                        'reservation': updated_reservation,
                        'formatted_datetime': formatted_datetime_updated,
                        'action': 'cancelled'
                    })
                else:
                    return render(request, 'ecosuite/reservation_error.html', {
                        'error_title': 'Update Failed',
                        'error_message': 'Failed to cancel the reservation. Please try again.'
                    })
            else:
                return render(request, 'ecosuite/reservation_error.html', {
                    'error_title': 'Invalid Action',
                    'error_message': "The action must be either 'confirm' or 'cancel'."
                })
        
        # No action provided, mark reservation as verified, then show the confirmation UI
        try:
            verify_update = {
                'status': 'verified',
                'updatedAt': timezone.now().isoformat()
            }
            verify_response = supabase.table('ecosuite_reservations').update(verify_update).eq('id', reservation_id).execute()

            if verify_response.data and len(verify_response.data) > 0:
                # Use the updated reservation data if available
                reservation = verify_response.data[0]
                formatted_datetime = format_reservation_datetime(reservation.get('reservationDateTime', 'N/A'))

            # After successful verification, trigger Koala broadcast if templateId is provided
                try:

                    trial_login_url = 'https://taratechapi.fly.dev/api/koalaplus/trial-login/'
                    trial_resp = requests.get(trial_login_url, timeout=5)
                    trial_data = trial_resp.json() if trial_resp.ok else {}
                    koala_token = (
                        trial_data.get('data', {})
                        .get('koalaToken', {})
                        .get('accessToken')
                    )

                    if koala_token:
                        # Prepare notification payload for Koala
                        customer_phone = reservation.get('customerPhone')
                        customer_name = reservation.get('customerName') or reservation.get('customer_name')
                        param_data = [
                            # customer_name or '',
                            # formatted_datetime
                        ]

                        koala_payload = {
                            'token': koala_token,
                            'campaignName': '007',
                            'templateId': '007',
                            'notificationData': [
                                {
                                    'phoneNumber': customer_phone,
                                    'paramData': param_data,
                                }
                            ],
                        }

                        # Fire-and-forget call to internal Koala broadcast endpoint
                        koala_broadcast_url = 'https://taratechapi.fly.dev/api/koalaplus/broadcast-reservation-success/'
                        try:
                            requests.post(
                                koala_broadcast_url,
                                json=koala_payload,
                                timeout=5,
                            )
                        except Exception:
                            # Do not block or error the confirmation flow if broadcast fails
                            pass
                except Exception:
                    # Swallow any Koala integration errors to keep confirmation flow robust
                    pass
        except Exception:
            # If verification update fails, continue to show the UI with original data
            pass

        return render(request, 'ecosuite/confirm_reservation.html', {
            'reservation': reservation,
            'formatted_datetime': formatted_datetime
        })
        
    except Exception as e:
        return render(request, 'ecosuite/reservation_error.html', {
            'error_title': 'Error',
            'error_message': str(e)
        })

def format_reservation_datetime(reservation_datetime):
    """Format reservation datetime for display."""
    try:
        # Parse and format datetime nicely
        dt = datetime.fromisoformat(reservation_datetime.replace('Z', '+00:00'))
        return dt.strftime('%A, %B %d, %Y at %I:%M %p')
    except:
        return reservation_datetime

