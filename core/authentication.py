from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from google.auth.transport import requests
from google.oauth2 import id_token
import json

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=400)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user_id': user.id,
            'username': user.username,
            'token': token.key
        }, status=201)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user_id': user.id,
                'username': user.username,
                'token': token.key
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=401)


class GoogleOAuthView(APIView):
    """
    API-only Google OAuth - Frontend sends Google ID token, backend validates and returns API token
    
    POST /api/google-auth/
    {
        "id_token": "google_id_token_from_frontend"
    }
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        print(f"DEBUG: Received request data: {request.data}")
        id_token_str = request.data.get('id_token')
        print(f"DEBUG: ID token: {id_token_str[:50] if id_token_str else 'None'}...")
        
        if not id_token_str:
            print("DEBUG: No id_token provided")
            return Response({
                'error': 'id_token is required'
            }, status=400)
        
        try:
            print("DEBUG: Attempting to verify Google token...")
            # Verify the Google ID token
            # Note: You'll need to add your Google OAuth Client ID here
            CLIENT_ID = "87725663952-833nil17edtc3v8p8i380ct1gs0960sf.apps.googleusercontent.com"
            
            idinfo = id_token.verify_oauth2_token(
                id_token_str, requests.Request(), CLIENT_ID
            )
            print(f"DEBUG: Token verified successfully: {idinfo}")
            
            # Extract user information from Google
            google_id = idinfo['sub']
            email = idinfo['email']
            name = idinfo.get('name', '')
            picture = idinfo.get('picture', '')
            print(f"DEBUG: User info - email: {email}, name: {name}")
            
            # Check if user already exists by email or create new one
            try:
                print(f"DEBUG: Looking for existing user with email: {email}")
                # Get the first user with this email (in case of duplicates)
                user = User.objects.filter(email=email).first()
                if user:
                    created = False
                    print(f"DEBUG: Found existing user: {user.username}")
                else:
                    # No user found with this email, create new one
                    print("DEBUG: User not found, creating new user...")
                    # Create new user with unique username
                    username = email
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{email}_{counter}"
                        counter += 1
                    print(f"DEBUG: Creating user with username: {username}")
                        
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        first_name=name.split(' ')[0] if name else '',
                        last_name=' '.join(name.split(' ')[1:]) if len(name.split(' ')) > 1 else '',
                    )
                    created = True
                    print(f"DEBUG: User created successfully: {user.id}")
            except Exception as e:
                print(f"DEBUG: Error in user lookup/creation: {e}")
                raise
            
            # Generate API token for the user
            print(f"DEBUG: Getting/creating token for user: {user.id}")
            token, token_created = Token.objects.get_or_create(user=user)
            print(f"DEBUG: Token ready: {token.key[:10]}...")
            
            response_data = {
                'success': True,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'name': name,
                'picture': picture,
                'token': token.key,
                'auth_method': 'google',
                'created': created  # True if new user, False if existing
            }
            print(f"DEBUG: Returning success response")
            return Response(response_data)
            
        except ValueError as e:
            print(f"DEBUG: ValueError occurred: {e}")
            return Response({
                'error': 'Invalid Google token',
                'details': str(e)
            }, status=400)
        except Exception as e:
            print(f"DEBUG: Unexpected error occurred: {type(e).__name__}: {e}")
            import traceback
            print(f"DEBUG: Full traceback: {traceback.format_exc()}")
            return Response({
                'error': 'Authentication failed',
                'details': str(e)
            }, status=500)
