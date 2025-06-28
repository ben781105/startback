from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import send_bulk_sms_task
from rest_framework.decorators import api_view,permission_classes
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # remove if you want to allow unauthenticated users
def send_sms(request):
    message = request.data.get('message')
    recipients = request.data.get('recipients')

    if not message or not recipients:
        return Response({'error': 'Both message and recipients are required.'}, status=400)

    send_bulk_sms_task.delay(message, recipients)
    return Response({'status': 'SMS queued for sending'})

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    return Response({
        "username": user.username,
        "email": user.email,
    })
