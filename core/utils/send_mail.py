from django.core.mail import send_mail



def order_mail(otp, email, first_name, last_name, username):
    email_template = render_to_string('mail/email_mail_reset_otp.html', {'first_name': first_name, 'last_name': last_name, 'otp': otp, 'username' : username})
    send_mail(
        'Reset your Password',
        '',
        'sender@example.com',
        [email],
        html_message=email_template,
    )