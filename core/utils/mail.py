from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from staffs.models import Staff

def send_confirmation_email(appointment):
    # Define the context for the email template
    context = {
        'fullname': appointment.fullname,
        'appointment_id': appointment.id,
        'saloon_name': appointment.saloon.name,
        'service_name': appointment.service.name,
        'staff_name': appointment.staff.name,
        'appointment_date': appointment.date,
        'start_time': appointment.start_time,
        'end_time': appointment.end_time,
        'total_price': appointment.total_price,
        'note': appointment.note,
    }

    # Render the HTML email template with the context
    html_message = render_to_string('appointment_confirmation_email.html', context)
    plain_message = strip_tags(html_message)  # Convert HTML to plain text

    subject = 'Appointment Booking Confirmation'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = appointment.email

    # Send the email
    send_mail(
        subject,
        plain_message,
        from_email,
        [to_email],
        html_message=html_message
    )

def staff_confirmation_email(appointment):
    context = {
        'fullname': appointment.fullname,
        'appointment_id': appointment.id,
        'saloon_name': appointment.saloon.name,
        'service_name': appointment.service.name,
        'staff_name': appointment.staff.name,
        'appointment_date': appointment.date,
        'start_time': appointment.start_time,
        'end_time': appointment.end_time,
        'total_price': appointment.total_price,
        'note': appointment.note,
    }
    html_message = render_to_string('staff_appointment_confirmation_email.html', context)
    plain_message = strip_tags(html_message)  # Convert HTML to plain text

    subject = 'Appointment Booking Confirmation'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = appointment.staff.email

    # Send the email
    send_mail(
        subject,
        plain_message,
        from_email,
        [to_email],
        html_message=html_message
    )


# def send_reminder_email(appointment):
#     # Define the context for the email template
#     context = {
#         'fullname': appointment.fullname,
#         'appointment_id': appointment.id,
#         'saloon_name': appointment.saloon.name,
#         'service_name': appointment.service.name,
#         'staff_name': appointment.staff.name,
#         'appointment_date': appointment.date,
#         'start_time': appointment.start_time,
#         'end_time': appointment.end_time,
#         'total_price': appointment.total_price,
#         'note': appointment.note,
#     }

#     # Render the HTML email template with the context
#     html_message = render_to_string('appointment_reminder_email.html', context)
#     plain_message = strip_tags(html_message)  # Convert HTML to plain text

#     subject = 'Appointment Reminder'
#     from_email = settings.DEFAULT_FROM_EMAIL
#     to_email = appointment.email

#     # Send the email
#     send_mail(
#         subject,
#         plain_message,
#         from_email,
#         [to_email],
#         html_message=html_message
#     )