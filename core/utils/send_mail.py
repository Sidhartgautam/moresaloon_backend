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

def send_subscription_confirmation_email(email):
    """
    Function to send subscription confirmation email.
    """
    subject = "Thank you for subscribing to our Newsletter"
    message = (
        "Hello,\n\n"
        "Thank you for subscribing to our newsletter! We'll keep you updated with the latest news.\n\n"
        "Best regards,\nThe MoreTrek Team"
    )
    recipient_list = [email]

    # Send email using Django's send_mail function
    send_mail(
        subject,
        message,
        'moretechglobal@gmail.com',  # Your sender email
        recipient_list,
        fail_silently=False,
    )