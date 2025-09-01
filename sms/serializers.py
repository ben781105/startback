from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ContactGroup, Contact
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password','phone_number']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class ContactSerializer(serializers.ModelSerializer):
    created_at= serializers.SerializerMethodField()
    class Meta:
        model = Contact
        fields = ['id','phone_number','created_at','group']

    def get_created_at(self, obj):
         return obj.created_at.strftime('%Y %m %d')


class ContactGroupSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)
    contact_count = serializers.IntegerField( read_only=True)

    class Meta:
        model = ContactGroup
        fields = ['id', 'name', 'contacts','contact_count']