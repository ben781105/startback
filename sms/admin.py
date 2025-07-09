from django.contrib import admin
from .models import SMSMessage,Contact,ContactGroup,SMSHistoryRecipient,SMSHistory

admin.site.register(SMSMessage)
admin.site.register(Contact)
admin.site.register(ContactGroup)
admin.site.register(SMSHistory)
admin.site.register(SMSHistoryRecipient)
