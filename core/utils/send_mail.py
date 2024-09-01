from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_appointment_confirmation_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        'sender@example.com',  # You can configure this email in settings
        recipient_list,
        fail_silently=False,
    )