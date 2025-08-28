from celery import shared_task
import africastalking
import os

@shared_task
def send_bulk_sms_task(message,recipients):
    africastalking.initialize(
        os.getenv("AFRICASTALKING_USERNAME"),
        os.getenv("AFRICASTALKING_API_KEY")
    )
    sms = africastalking.SMS
    response = sms.send(message, recipients)
    return response