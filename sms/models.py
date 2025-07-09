from django.db import models
from django.conf import settings

class ContactGroup(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name
    
class Contact(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    group = models.ForeignKey(ContactGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'phone_number') 

    def __str__(self):
        return f"{self.phone_number}"


class SMSMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    contacts = models.ManyToManyField(Contact, related_name='messages') 
    status = models.CharField(max_length=100, choices=[
        ('queued','QUEUED'),
        ('sent','SENT'),
        ('failed','FAILED'),
    ], default='queued')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.message[:30]}"


class SMSHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    recipients = models.JSONField()
    status = models.CharField(max_length=100,choices=[
        ('queued','QUEUED'),
        ('sent','SENT'),
        ('failed','FAILED'),
    ],default='queued')
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message[:30]}"
    
class SMSHistoryRecipient(models.Model):
    history = models.ForeignKey(SMSHistory, related_name='recipient_logs', on_delete=models.CASCADE)
    contact = models.ForeignKey('Contact', null=True, blank=True, on_delete=models.SET_NULL)
    phone_number = models.CharField(max_length=15)
    delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.phone_number} - Delivered: {self.delivered}"