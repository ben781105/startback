from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import send_bulk_sms_task
from rest_framework.decorators import api_view,permission_classes
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from .models import ContactGroup,SMSHistory,Contact
from .serializers import ContactGroupSerializer, ContactSerializer
from django.db import IntegrityError

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_sms(request):
    user = request.user
    message = request.data.get('message')
    recipients = request.data.get('recipients')  
    group_id = request.data.get('group_id')      

    if not message:
        return Response({'error': 'Message content is required.'}, status=400)

    phone_numbers = []

    
    if group_id:
        try:
            group = ContactGroup.objects.get(id=group_id, user=user)
            contacts = group.contacts.all()
            phone_numbers = [contact.phone_number for contact in contacts]
        except ContactGroup.DoesNotExist:
            return Response({'error': 'Group not found.'}, status=404)

    
    if recipients:
        if isinstance(recipients, str):
            recipients = [r.strip() for r in recipients.replace('\n', ',').split(',')]
        phone_numbers += recipients 

    
    if not phone_numbers:
        return Response({'error': 'No recipients provided.'}, status=400)

    
    send_bulk_sms_task.delay(message, phone_numbers)

    
    SMSHistory.objects.create(
        user=user,
        message=message,
        recipients=phone_numbers,
        status='queued',
    )

    return Response({'status': 'SMS queued for sending', 'total_recipients': len(phone_numbers)})

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    name = request.data.get('name')
    if not name:
        return Response({'error': 'Group name is required'}, status=400)
    
    group = ContactGroup.objects.create(user=request.user, name=name)
    return Response(ContactGroupSerializer(group).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_contact_to_group(request):
    group_id = request.data.get('group_id')
    phone_number = request.data.get('phone_number')

    try:
        group = ContactGroup.objects.get(id=group_id, user=request.user)
    except ContactGroup.DoesNotExist:
        return Response({'error': 'Group not found'}, status=404)

    try:
        contact = Contact.objects.create(
            user=request.user,
            phone_number=phone_number,
            group=group
        )
    except IntegrityError:
        return Response({'error': 'contact already exists'}, status=400)

    return Response(ContactSerializer(contact).data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_contact(request, contact_id):
    try:
        contact = Contact.objects.get(id=contact_id, user=request.user)
        contact.delete()
        return Response({'message': 'Contact deleted'})
    except Contact.DoesNotExist:
        return Response({'error': 'Contact not found'}, status=404)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_group(request, group_id):
    try:
        group = ContactGroup.objects.get(id=group_id, user=request.user)
        group.delete()
        return Response({'message': 'Group deleted'})
    except ContactGroup.DoesNotExist:
        return Response({'error': 'Group not found'}, status=404)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_group(request, group_id):
    try:
        group = ContactGroup.objects.get(id=group_id, user=request.user)
    except ContactGroup.DoesNotExist:
        return Response({'error': 'Group not found'}, status=404)

    new_name = request.data.get('name')
    if not new_name:
        return Response({'error': 'New name required'}, status=400)

    group.name = new_name
    group.save()
    return Response(ContactGroupSerializer(group).data)