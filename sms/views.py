
from rest_framework.response import Response
from .tasks import send_bulk_sms_task
from rest_framework.decorators import api_view,permission_classes
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from .models import ContactGroup,SMSHistory,Contact
from rest_framework.pagination import PageNumberPagination
from .serializers import ContactGroupSerializer, ContactSerializer
from django.db import IntegrityError
from django.db.models import Count
from django.core.paginator import Paginator


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_sms(request):
    user = request.user
    message = request.data.get('message')
    recipients = request.data.get('recipients')  
    group_ids = request.data.get('group_ids')      

    if not message:
        return Response({'error': 'Message content is required.'}, status=400)

    phone_numbers = []

    
    if group_ids:
        if isinstance(group_ids, int) or isinstance(group_ids, str):
            group_ids = [group_ids]  # normalize to list

        
        for gid in group_ids:
            try:
                group = ContactGroup.objects.get(id=gid, user=user)
                contacts = group.contacts.all()
                phone_numbers.extend([contact.phone_number for contact in contacts])
            except ContactGroup.DoesNotExist:
                return Response({'error': f'Group with id {gid} not found.'}, status=404)

    
    if recipients:
        if isinstance(recipients, str):
            recipients = [r.strip() for r in recipients.replace('\n', ',').split(',')]
        phone_numbers.extend(recipients)


    phone_numbers = list(set(phone_numbers))

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
        try:
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'error': 'Username or email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    return Response({
        "username": user.username,
        "email": user.email,
    })

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "page": self.page.number,  
            "page_size": self.get_page_size(self.request),
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    name = request.data.get('name')
    if not name:
        return Response({'error': 'Group name is required'}, status=400)
    
    group = ContactGroup.objects.create(user=request.user, name=name)
    serializer = ContactGroupSerializer(group)
    return Response(serializer.data, status=201)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_groups(request):
    user = request.user
    search_query = request.GET.get('search', '')

    groups = ContactGroup.objects.filter(user=user)

    if search_query:
        groups = groups.filter(name__icontains=search_query)

    
    groups = groups.annotate(contact_count=Count('contacts'))

    paginator = CustomPageNumberPagination()
    paginated_groups = paginator.paginate_queryset(groups, request)

    serializer = ContactGroupSerializer(paginated_groups, many=True)
    return paginator.get_paginated_response(serializer.data)

    

@api_view(['POST'])
@permission_classes([IsAuthenticated])

def add_contacts_to_group(request, group_id):
    phone_numbers = request.data.get('phone_numbers', [])  

    if  not phone_numbers:
        return Response({"error": "phone_numbers are required"}, status=400)

    try:
        group = ContactGroup.objects.get(id=group_id,user=request.user)
    except ContactGroup.DoesNotExist:
        return Response({"error": "Group not found"}, status=404)

    added_contacts = []
    for phone in phone_numbers:
        phone = phone.strip()
        if not phone:
            continue
        contact, _ = Contact.objects.get_or_create(phone_number=phone,user=request.user)
        group.contacts.add(contact)
        added_contacts.append(phone)

    return Response({
    "added_contacts": added_contacts,  
    "group": group.id
})


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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import SMSHistory


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sms_history(request):
    user = request.user
    search_query = request.GET.get('search', '')  # optional search query

    
    messages = SMSHistory.objects.filter(user=user)
    if search_query:
        messages = messages.filter(message__icontains=search_query)

    messages = messages.order_by('-sent_at')  # recent first

  
    paginator = PageNumberPagination()
    paginator.page_size = 10  
    result_page = paginator.paginate_queryset(messages, request)

    history = [
        {
            "message": sms.message,
            "number_of_recipients": len(sms.recipients) if sms.recipients else 0,
            "status": "Message pending sending" if sms.status == 'queued' else "Message not sent",
            "sent_at": sms.sent_at
        }
        for sms in result_page
    ]

    return paginator.get_paginated_response(history)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def contact_list(request):
    search_query = request.GET.get("search", "")
    page_number = request.GET.get("page", 1)
    page_size = int(request.GET.get("page_size", 10))

    contacts = Contact.objects.filter(user=request.user).order_by("-created_at")

    if search_query:
        contacts = contacts.filter(phone_number__icontains=search_query)

    paginator = Paginator(contacts, page_size)
    page_obj = paginator.get_page(page_number)

    serializer = ContactSerializer(page_obj, many=True)
    results = serializer.data

    for contact in results:
        if contact.get('created_at'):
            contact['created_at'] = contact['created_at'].replace(" ", "-")

    return Response({
        "count": paginator.count,
        "page_size":page_size,
        "page":page_number,
        "next": page_obj.has_next() and request.build_absolute_uri(f"?page={page_obj.next_page_number()}") or None,
        "previous": page_obj.has_previous() and request.build_absolute_uri(f"?page={page_obj.previous_page_number()}") or None,
        "results": results
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = request.user
    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone_number": user.phone_number,
        
    }
    return Response(data)