from django.db import models
from django.conf import settings

class SMSMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message= models.TextField()
    created_at =models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100,choices=[
        ('queued','QUEUED'),
        ('sent','SENT'),
        ('failed','FAILED'),
    ],default='queued')

    def __str__(self):
        return f'{self.message[:30]}'
    
class Recepient(models.Model):
    sms = models.ForeignKey(SMSMessage,related_name='recipients',on_delete=models.CASCADE)
    phone_number =models.CharField(max_length=15)
    delivered = models.BooleanField(default=False)

    def __str__(self):
        return self.phone_number

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
