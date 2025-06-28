from celery import shared_task
import africastalking

@shared_task
def send_bulk_sms_task(message,recipients):
    africastalking.initialize('sandbox','atsk_b69111d08e6995fb9fc31cca075f47c5bd3221eff28fe32c67baf8ca0337101cc5b6dc15')
    sms = africastalking.SMS
    response= sms.send(message,recipients)
    return response