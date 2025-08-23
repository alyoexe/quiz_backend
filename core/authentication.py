from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class RegisterView(APIView):
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
